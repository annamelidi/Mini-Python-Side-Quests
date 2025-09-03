import re
from operator import itemgetter

def parse_swissprot(file_path, fasta_topN=1000):
    proteins = {}  # {id: [charge, mw, charge_per_mw, seq]}

    with open(file_path, "r") as infile:
        seq_flag = False
        seq = ""
        prot_id = None
        mw = None
        charge = 0

        for line in infile:
            line = line.strip()

            # Match ID line
            id_match = re.match(r"^ID\s+(\S+)", line)
            if id_match:
                prot_id = id_match.group(1)

            # Match SQ line (sequence header with MW)
            elif line.startswith("SQ"):
                seq_flag = True
                sq_match = re.search(r"(\d+)\s+MW;", line)
                if sq_match:
                    mw = int(sq_match.group(1))
                seq = ""  # reset sequence

            # End of entry
            elif line == "//":
                seq_flag = False
                charge = 0
                for aa in seq.upper():
                    if aa in ("D", "E"):
                        charge -= 1
                    elif aa in ("K", "R", "H"):
                        charge += 1

                if prot_id and mw:
                    proteins[prot_id] = [charge, mw, charge / mw, seq]

                # reset for next entry
                prot_id, mw, seq, charge = None, None, "", 0

            # Sequence lines
            elif seq_flag:
                seq += line.replace(" ", "")

    # Write results to FASTA
    with open("fasta_top_charge.fasta", "w") as f1, open("fasta_top_charge_per_mw.fasta", "w") as f2:
        # Top N by charge
        top_by_charge = sorted(proteins.items(), key=lambda x: x[1][0], reverse=True)[:fasta_topN]
        for prot_id, (charge, mw, _, seq) in top_by_charge:
            f1.write(f">{prot_id} MW:{mw} Charge:{charge}\n")
            for i in range(0, len(seq), 60):
                f1.write(seq[i:i+60] + "\n")

        # Top N by charge/mw
        top_by_charge_per_mw = sorted(proteins.items(), key=lambda x: x[1][2], reverse=True)[:fasta_topN]
        for prot_id, (charge, mw, _, seq) in top_by_charge_per_mw:
            f2.write(f">{prot_id} MW:{mw} Charge:{charge}\n")
            for i in range(0, len(seq), 60):
                f2.write(seq[i:i+60] + "\n")


if __name__ == "__main__":
    parse_swissprot("test.txt", fasta_topN=3)  # change to 1000 for full task
