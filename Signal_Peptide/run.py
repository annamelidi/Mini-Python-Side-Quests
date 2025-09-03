import re

if __name__ == "__main__":
    # Example: get all mature protein sequences as a list instead of writing to file
    def get_mature_proteins(input_file):
        mature_proteins = []
        with open(input_file, "r") as infile:
            prot_id = None
            is_human = False
            has_signal = False
            has_propeptide = False
            peptide_end = None
            propeptide_end = None
            seq_flag = False
            aminoseq = ""

            for line in infile:
                line = line.rstrip("\n")

                id_match = re.match(r"ID\s+(\S+)", line)
                os_match = re.match(r"OS\s+(Homo sapiens)", line)
                signal_match = re.match(r"FT\s+SIGNAL\s+(\d+)\s+(\d+)", line)
                propep_match = re.match(r"FT\s+PROPEP\s+(\d+)\s+(\d+)", line)
                sq_match = re.match(r"SQ\s+SEQUENCE", line)

                if id_match:
                    prot_id = id_match.group(1)

                elif os_match:
                    is_human = True

                elif signal_match:
                    peptide_end = int(signal_match.group(2))
                    has_signal = True

                elif propep_match and has_signal:
                    propeptide_end = int(propep_match.group(2))
                    has_propeptide = True

                elif sq_match and is_human and has_signal:
                    seq_flag = True
                    aminoseq = ""

                elif line == "//":
                    if is_human and has_signal and aminoseq:
                        aminoseq_premature = aminoseq.replace(" ", "")
                        if not has_propeptide:
                            aminoseq_mature = aminoseq_premature[peptide_end-1:]
                        else:
                            aminoseq_mature = aminoseq_premature[propeptide_end-1:]
                        mature_proteins.append((prot_id, aminoseq_mature))
                    prot_id = None
                    is_human = False
                    has_signal = False
                    has_propeptide = False
                    peptide_end = None
                    propeptide_end = None
                    seq_flag = False
                    aminoseq = ""
                elif seq_flag:
                    aminoseq += line.strip()
            
        # Save mature proteins in FASTA format
        with open("mature_proteins.fasta", "w") as fasta_out:
            for prot_id, seq in mature_proteins:
                fasta_out.write(f">{prot_id}\n")
            # Write sequence in lines of 60 characters
            for i in range(0, len(seq), 60):
                fasta_out.write(seq[i:i+60] + "\n")
        return mature_proteins

    # Example usage:
    proteins = get_mature_proteins("test.txt")
    print(f"Extracted {len(proteins)} mature proteins.")
