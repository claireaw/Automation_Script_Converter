import csv

input_file = "Input.log"
output_file = "Output.csv"

with open(input_file, "r") as infile, open(
    output_file, "w", newline=""
) as outfile:

    writer = csv.writer(outfile)

    # Headers
    writer.writerow([
        "Source Voltage",
        "Source Int Voltage",
        "Source Current",
        "Drain Voltage",
        "Drain Int Voltage",
        "Drain Current",
        "Gate Voltage",
        "Gate Int Voltage",
        "Gate Current",
    ])

    for line in infile:
        line = line.strip()

        # Only process Silvaco data lines
        if line.startswith("d "):
            values = line.split()[1:]
            writer.writerow(values)

print(f"Conversion complete: {output_file}")