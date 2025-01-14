# GoodData.CN Foreign Data Wrapper

## Getting Started

For convenience a `Dockerfile` is in place which when started will run `PostgreSQL 12` with `multicorn` and `gooddata-fdw`
installed.

For even better user experience we prepared `docker-compose.yaml` file, which contains both `gooddata-fdw` and `gooddata-cn-ce` services.
If you execute (in this folder):
``` shell
docker-compose up -d
```
gooddata-fdw image is built from the Dockerfile and both services are started in background.
Note: services in docker-compose.yaml contain setup of various environment variables including `POSTGRES_PASSWORD`.
Set the variables in your environment if you want to, before you execute the above command.
Default value for`POSTGRES_PASSWORD` is `gooddata123`.

You can also execute:
``` shell
docker-compose build
```
to rebuild the fdw image.

If you would like to purge a container completely (including the volume) and start from scratch, you can use a helper script:
```
./rebuild.sh gooddata-cn-ce
./rebuild.sh gooddata-fdw
```

Before you start playing with gooddata-fdw, fill the gooddata-cn-ce with a content (LDM, metrics, insights).
E.g you can follow our [Getting Started documentation](https://www.gooddata.com/developers/cloud-native/doc/1.5/getting-started/).

After the `gooddata-fdw` container starts, you can connect to the running PostgreSQL:

-   From console using `psql --host localhost --port 2543 --user gooddata gooddata`

    You will be asked to enter the password that you have specified when starting the script.

-   From any other client using JDBC string: `jdbc:postgresql://localhost:2543/gooddata`

    You will be asked to enter username (gooddata) and password.

Once connected you will be able to work with the GD.CN Foreign Data Wrapper.
At first, you need to define your GD.CN server in PostgreSQL:

```postgresql
CREATE SERVER multicorn_gooddata FOREIGN DATA WRAPPER multicorn
OPTIONS (
    wrapper 'gooddata_fdw.GoodDataForeignDataWrapper',
    host 'https://gooddata-cn-ce:3000', -- host equal to name of container with GD.CN.CE
    token 'YWRtaW46Ym9vdHN0cmFwOmFkbWluMTIz' -- default gooddata-cn-ce token, documented in public DOC as well
);
```

As of now GD.CN community edition (single container deployment) does support only `localhost` as target host.
If you spin-up GD.CN and FDW using docker-compose, GD.CN host equals to the service name in the docker-compose, e.g. `gooddata-cn-ce`.
To enable such setup, we provide an option `header_host`:
```postgresql
CREATE SERVER multicorn_gooddata FOREIGN DATA WRAPPER multicorn
  OPTIONS (
    wrapper 'gooddata_fdw.GoodDataForeignDataWrapper',
    host 'http://gooddata-cn-ce:3000', -- host equal to name of container with GD.CN.CE
    token 'YWRtaW46Ym9vdHN0cmFwOmFkbWluMTIz', -- default gooddata-cn-ce token, documented in public DOC as well
    headers_host 'localhost'
  );
```

Typically, you have to do this once per GD.CN installation. You can add as many servers as you want/need.

**IMPORTANT**: do not forget to specify host including the schema (http or https).

## Import GoodData objects as foreign tables into Postgres schema

You can import insights created in GoodData.CN Analytical Designer as PostgreSQL foreign tables.
You can import insights from as many workspaces and / or GoodData.CN instances (servers) as you want.

You can also import your entire semantic model including MAQL metrics into a special `compute` **pseudo-table**.
Doing SELECTs from this table will trigger computation of analytics on your GoodData.CN server based on the columns
that you have specified on the SELECT.

Note that the `compute` is called pseudo-table for a reason. It does not adhere to the relational model. The columns
that you SELECT map to facts, metrics and labels in your semantic model. Computing results for the select will automatically
aggregate results on the columns that are mapped to labels in your semantic model. In other words cardinality of
the `compute` table changes based on the columns that you SELECT.

For your convenience we prepared a stored procedure, which:
- (re)creates target schema
- imports currently existing insights and/or entire semantic model

You can re-execute the procedure to update foreign tables.

```postgresql
-- This maps all insights stored in GD.CN workspace `workspace_id` into the Postgres schema named `workspace_id`
CALL import_gooddata('workspace_id', 'insights');
-- By utilizing the third parameter you can override the name of the target Postgres schema
CALL import_gooddata('workspace_id', 'insights', 'custom_schema');

-- This imports the semantic model into the 'compute' pseudo-table.
CALL import_gooddata('workspace_id', 'compute');

-- This imports both insights and compute
CALL import_gooddata('workspace_id', 'all');

-- This is how you can extend max size of numeric columns in foreign tables (basically to support larger numbers)
CALL import_gooddata(workspace := 'goodsales', object_type := 'all', numeric_max_size := 24);

-- Specify custom foreign server name - this enables you importing from multiple servers into the same FDW instance
CALL import_gooddata(workspace := 'goodsales', object_type := 'all', foreign_server := 'multicorn_gooddata_stg');
```

Default max numeric size is 18, default digits after decimal point is 2 unless metric format defines more.

You will get couple of 'NOTICE' messages as the import progresses. You can then check the imported tables for instance
by executing:

```postgresql
SELECT * FROM information_schema.foreign_tables WHERE foreign_table_schema = 'workspace_id';
```

**IMPORTANT**: Your semantic model may consist of multiple isolated segments that have no relationship between them. Attempting
to compute results from multiple isolated segments will result in errors.

## Custom reports as foreign tables

You can manually create your own foreign tables and map their columns to GoodData.CN semantic model. This is similar
to creating normal tables except you have to provide table and column OPTIONS to establish the correct mapping. For instance:

```postgresql
CREATE FOREIGN TABLE custom_report (
    some_label VARCHAR OPTIONS (id 'label/some_label'),
    some_fact_sum  NUMERIC(15,5) OPTIONS (id 'fact/some_fact', agg 'sum'),
    some_fact_avg  NUMERIC(15,5) OPTIONS (id 'fact/some_fact', agg 'avg'),
    some_metric  NUMERIC(15,5) OPTIONS (id 'metric/some_metric')
)
SERVER multicorn_gooddata
OPTIONS ( workspace 'workspace_id');
```

To explain:

-  OPTIONS on foreign table must contain identifier of workspace to map to
-  OPTIONS on each column must contain identifier of semantic model entity. The id is string but consisting
   of two parts `<entity_type>/<entity_id>`. Where `entity_type` is either label, fact or metric.

For columns that map to facts in your semantic model, you can also specify what aggregation function should be used when
aggregating the fact values for the labels in your custom report table. You can use the following aggregation functions:

-  `sum`
-  `avg`,
-  `min`,
-  `max`,
-  `median`

The `agg` key is optional. If you do not specify it, then default 'sum' aggregation will be used. The value of `agg` is
case insensitive.

Note: If you do not specify the required options, the CREATE command will fail. If you specify wrong entity IDs,
the failures will happen at SELECT time.

## Push down of filters

When querying foreign tables, you can add WHERE clause filtering the result.
Due to performance reasons, it makes sense to push such filters down to the GD.CN, so not all data must be collected.

We are able to push only some filters down to the GD.CN:
- Simple attribute(label) filters
  - Example: `WHERE region IN ('East', 'West')`
- Simple date filters
  - Only DAY granularity is supported
  - (NOT) IN operator is `not` supported
  - Example: `WHERE my_date BETWEEN '2021-01-01 AND 2021-02-01`

If you use OR between conditions, it is not pushed down.
Push down is possible in case of custom tables and `compute` table, not in case of foreign tables imported from `insights`.

## Known limitations

It is not possible to reference a column in WHERE clause, which is not used in SELECT section.
Example:
```sql
SELECT label1, metric FROM insight WHERE label2 = 'a';
SELECT label1, metric FROM compute WHERE label2 = 'a'
```

While it is obvious in case of `insight` (it does not contain the column at all), in case of `compute` we would like to support it,
but we are not allowed due to lack of functionality in Multicorn -
the filter is always applied on final result set and if it does not contain the column, it does not work.
