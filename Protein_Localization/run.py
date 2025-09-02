import re

def parse_swissprot_stream(input_file, output_file):
    entry_lines = []
    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        for line in infile:
            if line.startswith("//"):
                process_entry("".join(entry_lines), outfile)
                entry_lines = []
            else:
                entry_lines.append(line)
        # Process last entry
        if entry_lines:
            process_entry("".join(entry_lines), outfile)

def process_entry(entry_text, outfile):
    # SwissProt ID
    id_match = re.search(r'^ID\s+(\S+)', entry_text, re.MULTILINE)
    if not id_match:
        return
    sp_id = id_match.group(1)

    # Organism
    if not re.search(r'^OS\s+Homo sapiens', entry_text, re.MULTILINE):
        return

    # Sequence
    seq_match = re.search(r'SQ\s+SEQUENCE\s+\d+\s+AA;.*\n((?:\s+[A-Za-z ]+\n)+)', entry_text, re.MULTILINE)
    if not seq_match:
        return
    sequence = "".join(seq_match.group(1).split())

    # Subcellular locations
    cc_match = re.search(r'CC   -!- SUBCELLULAR LOCATION:(.*?)(?=CC   -!-|\Z)', entry_text, re.DOTALL)
    if not cc_match:
        return
    cc_text = cc_match.group(1)
    locations = re.findall(r'([A-Za-z\s-]+)\s*\{ECO:0000269', cc_text)
    if len(locations) < 2:
        return

    # Write FASTA
    outfile.write(f">{sp_id}\n{sequence}\n")

if __name__ == "__main__":
    parse_swissprot_stream("test_uniprot_sprot.dat", "fasta.txt")
