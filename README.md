# datasette-annotate

[![PyPI](https://img.shields.io/pypi/v/datasette-annotate.svg)](https://pypi.org/project/datasette-annotate/)
[![Changelog](https://img.shields.io/github/v/release/MischaU8/datasette-annotate?include_prereleases&label=changelog)](https://github.com/MischaU8/datasette-annotate/releases)
[![Tests](https://github.com/MischaU8/datasette-annotate/workflows/Test/badge.svg)](https://github.com/MischaU8/datasette-annotate/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/MischaU8/datasette-annotate/blob/main/LICENSE)

Datasette plugin for annotating / labelling your training data.

## Installation

Install this plugin in the same environment as Datasette.

    datasette install datasette-annotate

Only the [root actor](https://docs.datasette.io/en/stable/authentication.html#using-the-root-actor) will have access to create (write) annotations.

## Usage

You can start the annotation process by going to the `/database_name/table_name/-/annotate` page. This table should be configured to specify which annotation labels can be selected, see below. Annotations will be written to the table `table_name_annotations`.

### Configuration

To add annotations for a table it must have a primary key column. The possible labels for each table should be configured by adding the following settings to the `metadata.json`:

```json
{
    "databases": {
        "my_database": {
            "tables": {
                "training_data": {
                    "plugins": {
                        "datasette-annotate": {
                            "labels": ["ABSTAIN", "HAM", "SPAM"]
                        }
                    }
                }
            }
        }
    }
}
```

If you are using `metadata.yml` the configuration should look like this:

```yaml
databases:
  my_database:
    tables:
      training_data:
        plugins:
          datasette-annotate:
            labels:
              - ABSTAIN
              - HAM
              - SPAM
```

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:

    cd datasette-annotate
    python3 -m venv venv
    source venv/bin/activate

Now install the dependencies and test dependencies:

    pip install -e '.[test]'

To run the tests:

    pytest
