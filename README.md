# csvwrangler

A CLI tool for quick CSV transformations, filtering, and summarization without writing code.

---

## Installation

```bash
pip install csvwrangler
```

Or install from source:

```bash
git clone https://github.com/yourname/csvwrangler.git
cd csvwrangler && pip install -e .
```

---

## Usage

```bash
# View a summary of your CSV file
csvwrangler summary data.csv

# Filter rows where column "age" is greater than 30
csvwrangler filter data.csv --where "age > 30"

# Select specific columns
csvwrangler select data.csv --cols "name,age,email"

# Sort by a column
csvwrangler sort data.csv --by "age" --desc

# Export transformed output to a new file
csvwrangler filter data.csv --where "country == 'US'" --out output.csv
```

### Example

```bash
$ csvwrangler summary sales.csv

Rows:    1,204
Columns: 8
Missing: 3 values across 2 columns

Column        Type     Min     Max     Mean
----------    ------   -----   -----   -----
revenue       float    10.5    9823.0  542.3
region        string   -       -       -
```

---

## Features

- Filter, sort, and select columns with simple flags
- Summarize datasets instantly
- Chain transformations via piped commands
- Zero dependencies beyond the standard library

---

## License

MIT © 2024 csvwrangler contributors