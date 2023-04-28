from datasette import hookimpl
from datasette.views.base import DatasetteError
from datasette.utils.asgi import Forbidden, Response


@hookimpl
def permission_allowed(actor, action):
    # TODO
    if action == "annotate" and actor and actor.get("id") == "root":
        return True


@hookimpl
def register_routes(datasette):
    # importing here to prevent circular dependency
    from datasette.views.row import RowView

    class AnnotateView(RowView):
        name = "annotate"

        async def data(self, request, default_labels=False):
            data, template_data, templates = await super().data(request, default_labels)
            return (data, template_data, ("datasette_annotate/annotate-row.html",) + templates)

        async def post(self, request, *args, **kwargs):
            # TODO permissions
            # await self.ds.ensure_permissions(request.actor, ["annotate-row"])

            db_name = request.url_vars["database"]
            table = request.url_vars["table"]
            pks = request.url_vars["pks"]
            post_vars = await request.post_vars()
            label = post_vars["label"]

            print(f"RECORD {db_name}/{table}/{pks} LABEL {label}")

            # TODO persist annotation

            datasette = self.ds
            datasette.add_message(request, f"Annotation for #{pks} is {label}", datasette.INFO)

            redirect_url = datasette.urls.table(db_name, table) + "/-/annotate"
            return Response.redirect(redirect_url)

    return [
        (r"^/(?P<database>[^/]+)/(?P<table>[^/]+)/-/annotate$", annotate_next_task),
        (r"^/(?P<database>[^/]+)/(?P<table>[^/]+)/(?P<pks>[^/]+)(\.(?P<format>\w+))?/-/annotate$", AnnotateView.as_view(datasette)),
    ]


@hookimpl
def extra_template_vars(datasette, database, table, view_name):
    if view_name == "annotate":
        # TODO insert annotation lables from configuration
        config = datasette.plugin_config(
            "datasette-annotate", database=database, table=table
        )
        if not config:
            # TODO show error?
            print("NO CONFIG")
            return None

        # TODO escape labels for CSS selectors
        return {
            "annotation_labels": config.get("labels", [])
        }


async def annotate_next_task(scope, receive, datasette, request):
    # TODO permissions
    # await self.ds.ensure_permissions(request.actor, ["annotate-row"])

    # TODO create annotations table if it doesn't exist

    db_name = request.url_vars["database"]
    table = request.url_vars["table"]
    print(f"db={db_name} table={table}")

    # XXX replace with datasette.resolve_table once 1.0 is released
    # db, table, is_view = datasette.resolve_table(request)

    db = datasette.get_database(db_name)
    pks = await db.primary_keys(table)
    print(f"PKS: {pks}")
    # TODO support compound primary keys
    if len(pks) != 1:
        raise DatasetteError("Compound primary keys are not supported")
    pk = pks[0]

    results = await db.execute(f"select {pk} from {table} order by random() limit 1")
    # TODO where not in annotations
    random_row_id = results.single_value()

    # TODO handle no more rows to annotate
    redirect_url = datasette.urls.row(db_name, table, random_row_id) + "/-/annotate"
    return Response.redirect(redirect_url)
