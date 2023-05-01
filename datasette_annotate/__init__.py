import sys
import textwrap

from datasette import hookimpl
from datasette.database import MultipleValues
from datasette.views.base import DatasetteError
from datasette.utils.asgi import Forbidden, NotFound, Response


@hookimpl
def permission_allowed(actor, action):
    if action == "annotate-row" and (
        (actor and actor.get("id") == "root") or (sys.platform == "emscripten")
    ):
        # running in Pyodide or other Emscripten based build
        return True


async def _ensure_annotations_table(db, table):
    # create annotations table if it doesn't exist
    await db.execute_write(
        textwrap.dedent(
            f"""
        create table if not exists {table}_annotations (
            doc_pk integer,
            created_at text,
            actor text,
            label text,
            comment text
        );
        """
        )
    )


async def get_pk_name(db, table):
    # TODO support compound primary keys
    pks = await db.primary_keys(table)
    if len(pks) != 1:
        raise DatasetteError("Compound primary keys are not supported")
    return pks[0]


def get_actor_id(request):
    if request.actor and "id" in request.actor:
        actor_id = request.actor.get("id")
    else:
        actor_id = None
    return actor_id


async def add_annotation(db, table, doc_pk, actor, label, comment=None):
    # create annotations table if it doesn't exist
    await _ensure_annotations_table(db, table)

    # persist annotation
    await db.execute_write(
        textwrap.dedent(
            f"""
        insert into {table}_annotations (doc_pk, created_at, actor, label, comment)
        values (:doc_pk, DATETIME('now'), :actor, :label, :comment)
        """
        ),
        {"doc_pk": doc_pk, "actor": actor, "label": label, "comment": comment},
    )


@hookimpl
def register_routes(datasette):
    # importing here to prevent circular dependency
    from datasette.views.row import RowView

    class AnnotateView(RowView):
        name = "annotate"

        async def data(self, request, default_labels=False):
            if not await datasette.permission_allowed(
                request.actor, "annotate-row", default=False
            ):
                raise Forbidden("Permission denied for annotate-row")
            data, template_data, templates = await super().data(request, default_labels)
            return (
                data,
                template_data,
                ("datasette_annotate/annotate-row.html",) + templates,
            )

        async def post(self, request, *args, **kwargs):
            datasette = self.ds
            if not await datasette.permission_allowed(
                request.actor, "annotate-row", default=False
            ):
                raise Forbidden("Permission denied for annotate-row")

            db_name = request.url_vars["database"]
            table = request.url_vars["table"]
            pk_value = request.url_vars["pks"]
            actor_id = get_actor_id(request)
            post_vars = await request.post_vars()
            label = post_vars.get("label")
            comment = post_vars.get("comment")

            config = datasette.plugin_config(
                "datasette-annotate", database=db_name, table=table
            )
            if not config:
                raise DatasetteError("Table not configured for annotations")

            # print(f"RECORD {db_name}/{table}/{pk_value} LABEL {label} BY {actor_id}")
            success = False

            if not label:
                message = f"Skipped annotation for #{pk_value} as label was missing."
            else:
                if label not in config.get("labels", []):
                    raise DatasetteError(f"Label {label} not supported")

                db = datasette.get_database(db_name)

                # persist annotation
                await add_annotation(db, table, pk_value, actor_id, label, comment)
                message = f"Annotated #{pk_value} as {label}."
                success = True

            datasette.add_message(
                request, message, datasette.INFO if success else datasette.WARNING
            )
            return Response.redirect(
                datasette.urls.table(db_name, table) + "/-/annotate"
            )

    return [
        (r"^/(?P<database>[^/]+)/(?P<table>[^/]+)/-/annotate$", annotate_next_task),
        (
            r"^/(?P<database>[^/]+)/(?P<table>[^/]+)/(?P<pks>[^/]+)(\.(?P<format>\w+))?/-/annotate$",
            AnnotateView.as_view(datasette),
        ),
    ]


@hookimpl
def extra_template_vars(datasette, database, table, view_name):
    if view_name == "annotate":
        # insert annotation lables from configuration
        config = datasette.plugin_config(
            "datasette-annotate", database=database, table=table
        )
        if not config:
            return None

        # TODO escape labels for CSS selectors
        return {"annotation_labels": config.get("labels", [])}


async def annotate_next_task(scope, receive, datasette, request):
    if not await datasette.permission_allowed(
        request.actor, "annotate-row", default=False
    ):
        raise Forbidden("Permission denied for annotate-row")

    db_name = request.url_vars["database"]
    table = request.url_vars["table"]

    # XXX replace with datasette.resolve_table once 1.0 is released
    # db, table, is_view = datasette.resolve_table(request)

    db = datasette.get_database(db_name)
    pk = await get_pk_name(db, table)

    await _ensure_annotations_table(db, table)
    results = await db.execute(
        textwrap.dedent(
            f"""
        select {pk} from {table} where {pk} not in (
            select doc_pk from {table}_annotations)
        order by random() limit 1
        """
        )
    )

    try:
        random_row_id = results.single_value()
    except MultipleValues:
        raise NotFound("No (more) documents found to annotate.")
    return Response.redirect(
        datasette.urls.row(db_name, table, random_row_id) + "/-/annotate"
    )
