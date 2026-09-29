import csv
import math
import pandas as pd
import sys

def conversion():
    input_file_transfer_5v = "Inputs/transfer_5v.log"
    input_file_transfer_p1v = "Inputs/transfer_0p1v.log"
    input_file_output_highv = "Inputs/output_highv.log"
    input_file_output_lowv = "Inputs/output_lowv.log"
    output_file_transfer_5v = "Outputs/transfer_5v.csv"
    output_file_transfer_0pv = "Outputs/transfer_0pv.csv"
    output_file_output_highv = "Outputs/output_highv.csv"
    output_file_output_lowv = "Outputs/output_lowv.csv"

    input_file_array = [input_file_transfer_5v, input_file_transfer_p1v, input_file_output_lowv, input_file_output_highv]
    output_file_array = [output_file_transfer_5v, output_file_transfer_0pv,output_file_output_lowv,output_file_output_highv]

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

def cutoff():
    j = 0
    #attempt to find
    df = pd.read_csv('Outputs/transfer_0pv.csv')
    for value in df['Drain Current']:
        #semi-arbitrary value
        if value <= 1E-15:
            cutoff = df.iat[j, 6]
            break
        else:
            cutoff = None
        j +=1
    if cutoff is None:
        print("No cutoff voltage found")
        sys.exit("No cutoff voltage found")
    print(f"Cutoff voltage: {cutoff}")

def ron(radius):
    df = pd.read_csv('Outputs/output_lowv.csv')
    smallV = df.iat[len(df['Drain Current'])-1, 5]
    Ron = (smallV/0.1)**-1
    print(f"Ron voltage: {Ron}")
    Ronsp = Ron*math.pi*((radius*1e-7)**2)
    print(f"Ron,sp voltage: {Ronsp}")

def modratio():
    df = pd.read_csv('Outputs/transfer_5v.csv')
    low = df.iat[0, 5]
    high = df.iat[22, 5]
    modratio = low/high
    print(f"Mod ratio voltage: {modratio}")

#dc
def maxIG():
    df = pd.read_csv("Outputs/transfer_5v.csv")
    mask = (df["Gate Voltage"] >= -10) & (df["Gate Voltage"] <= 0)
    max_ig = df.loc[mask, "Gate Current"].abs().max()
    print(f"Max |IG|: {max_ig:.3e} A")
    return max_ig

def leakage(max_ig):
    df = pd.read_csv("Outputs/output_highv.csv")
    #adjust and round for point at 90% of column length
    column_length = len(df['Drain Voltage'])
    column_length_point = round(column_length*.9)
    idss = df.at[column_length_point, 'Drain Current']
    leakage = max_ig/(idss)
    print(f"Leakage voltage: {leakage}")

def main():
    radius = int(input("Radius of channel (nm): "))
    conversion()
    cutoff()
    ron(radius)
    modratio()
    max_ig = maxIG()
    leakage(max_ig)

if __name__ == "__main__":
    main()