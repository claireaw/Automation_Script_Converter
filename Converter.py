import csv
import pandas as pd

def cutoff():
    cutoff = 0
    j = 0
    df = pd.read_csv('Outputs/transfer_0pv.csv')
    for value in df['Drain Current']:
        #semi-arbitrary value
        if value <= 1E-15:
            cutoff = df.iat[j, 6]
            break
        else:
            cutoff = None
        j +=1
    print(f"Cutoff voltage: {cutoff}")

def conversion():
    input_file_transfer_5v = "Inputs/transfer_5v.log"
    input_file_transfer_p1v = "Inputs/transfer_0p1v.log"
    input_file_output_lowv = "Inputs/output_lowv.log"
    output_file_transfer_5v = "Outputs/transfer_5v.csv"
    output_file_transfer_0pv = "Outputs/transfer_0pv.csv"
    output_file_output_lowv = "Outputs/output_lowv.csv"

    input_file_array = [input_file_transfer_5v, input_file_transfer_p1v, input_file_output_lowv]
    output_file_array = [output_file_transfer_5v, output_file_transfer_0pv,output_file_output_lowv]

    for i in range(0, len(input_file_array)):
        with open(input_file_array[i], "r") as infile, open(
            output_file_array[i], "w", newline=""
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

        print(f"Conversion complete: {output_file_array[i]}")

        with open(output_file_array[i], "r") as outfile:
            reader = csv.reader(outfile)

def Ron():
    df = pd.read_csv('Outputs/output_lowv.csv')
    smallV = df.iat[12, 5]
    print(smallV)
    Ron =

def main():
    conversion()
    cutoff()
    Ron()

if __name__ == "__main__":
    main()