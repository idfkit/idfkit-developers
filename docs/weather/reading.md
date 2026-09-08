# How to read a weather file

You have the text of an EPW file, retrieved by [downloading a
station's files](downloads.md) or read off disk. This guide turns it into the
header records and the hourly table, and computes monthly figures from it
without treating an unmeasured hour as a number.

Reading is the same operation in both languages and is spelled the same way. The
retrieval that precedes it is not: Python hands you a path and TypeScript hands
you text, for the reasons [How to download weather files](downloads.md) sets
out. None of that reaches a reader whose input comes from the caller, which is
why this page has one set of instructions rather than two.

{{ parity("weather-file-reading") }}

!!! info "In JavaScript, weather is a separate install"
    `pip install idfkit` installs weather support and its station index
    unconditionally. `npm install idfkit` installs neither. Add `@idfkit/weather`
    by name. The reader lives on the portable surface of that package, not on
    `@idfkit/weather/node`: it takes a string and touches no disk, so it runs in
    a browser tab, a worker or an edge runtime as readily as in Node.

## Read the file

=== "Python"

    ```python
    --8<-- "docs/snippets/weather/reading/read_an_epw.py:example"
    ```

=== "TypeScript"

    ```ts
    --8<-- "docs/snippets/js/weather/reading/read_an_epw.ts:example"
    ```

`parse_epw` / `parseEpw` takes text. Each language also has the source-taking
form for a path, `load_epw` and `loadEpw`, which reads the bytes, decodes them
as the weather formats are written, and adds nothing else. In TypeScript that
one is in `@idfkit/weather/node`, because it is the half that touches a disk.

## Reach a field by its name, never by its position

An EPW row is thirty-five comma-separated fields with no header line, so a
caller reading one positionally counts to it. The reader does that once and
gives every field a name: `dry_bulb_temperature` / `dryBulbTemperature`,
`relative_humidity` / `relativeHumidity`, `wind_speed` / `windSpeed`, and so on
for every column of the format.

Two fields are text and stay text. The source-and-uncertainty flags are
obviously so. The present weather codes are not: they hold a nine-digit value
such as `999999999`, which is nine single-digit observations written side by
side rather than a number near a billion. Coercing that yields a column of
meaningless integers, so it is never parsed.

!!! warning "Hour 24 is the last hour of its own day"
    The `hour` column runs 1 to 24, not 0 to 23. Hour 24 belongs to the day its
    row names, not to midnight of the next one. A chart that assumes otherwise is
    off by one for every day of the year and looks right until somebody checks a
    single value against the file.

## A measurement that was not taken is not a number

EPW has no blanks. A station that never measured a quantity writes a reserved
value in the slot, so a file that never recorded its albedo carries `999.000` in
that column for all 8,760 hours. Averaged naively, that is a plausible-looking
number that is wrong by three orders of magnitude.

Both libraries map those values to an absent value instead, per field and per
value, from the reserved-value table published in the EnergyPlus Weather File
Data Dictionary and committed once for both languages.

=== "Python"

    ```python
    --8<-- "docs/snippets/weather/reading/absent_values.py:example"
    ```

=== "TypeScript"

    ```ts
    --8<-- "docs/snippets/js/weather/reading/absent_values.ts:example"
    ```

Absence is `nan` in Python and `NaN` in TypeScript. That is chosen rather than
convenient: no physical quantity in this format can be nan and no EPW can
express one, so it is not a value the column could otherwise have held. It is
therefore distinguishable from a real zero, which matters because zero solar
radiation at night is a measurement, and it propagates loudly through arithmetic
instead of quietly biasing a result.

!!! warning "A reserved value is not the same as a large number"
    Ceiling height reserves three values: `99999` for a measurement that was not
    made, `77777` for an unlimited ceiling, and `88888` for a cirroform ceiling.
    The last two are observations. Across the sampled corpus that column holds
    `77777` in 55% of its rows and `99999` in none, so a reader applying the rule
    "a large number means missing" blanks more than half of it and reports a real
    sky condition as unmeasured. The table is per field and per value for exactly
    this reason.

## Compute a monthly figure

`monthly_means` / `monthlyMeans` returns twelve entries for one column, January
first, each carrying the mean and the count of hours that went into it.

The count is part of the answer rather than something to derive from it. Without
it you cannot tell a mean over 744 hours from a mean over three, and both look
like numbers.

The mean excludes absent hours from the sum **and from the divisor**, so it is
the mean of the values that exist rather than their sum spread over hours that do
not. A month in which every hour is absent gives an absent mean with a count of
zero, which is distinguishable from a month whose mean is genuinely zero.

## What the reader does not do

- **Write an EPW.** Reading only.
- **Interpret the design conditions record.** It is kept as text. The DDY member
  of the same archive is the supported path to design conditions; see [How to
  apply design days](design-days.md).
- **Read the climate summary.** The `.stat` member of an archive is a report
  written for a person, in around forty section shapes whose set varies with the
  station's climate. Parsing it would be brittle in a way this reader is not, and
  every figure it carries is derivable from the EPW itself. It is used as an
  oracle in the shared conformance corpus, where a brittle parse is somebody's
  offline maintenance task rather than something in a caller's path, and that is
  the only place it is read.
- **Interpolate, gap-fill or repair.** An absent value is reported as absent.
  What to do about it depends on what you are computing, which makes it your
  judgement rather than the reader's.
- **Guess at what it cannot represent.** A file whose rows disagree with its own
  declared data period fails, naming the disagreement. So does a row with the
  wrong field count, naming the row. Nothing partial is ever returned.

## How the two languages are held to the same answer

Both readers are checked against the climate summary the EnergyPlus Weather
Converter produced from the same archive, in the shared conformance corpus rather
than in either library's own tests. That summary is not written by either library
and ships in the same archive as the file it describes, so the expectation and the
input cannot drift apart.

The check compares monthly means of dry bulb, dew point, relative humidity and
wind speed over six stations spanning the climate range, and separately asserts
that the reserved values in a seventh file read as absent. Beyond the four fields
the summary aggregates, the two libraries are held only to agreeing with each
other, which is weaker; the corpus says so rather than implying the whole table
is checked against something external.
