import warnings

def _floatify_list(LIST):
	temp = []
	for i in range(len(LIST)):
		try:
			temp.append(float(LIST[i]))
		except ValueError:
			temp.append(LIST[i])
	return temp

def load_audit_file(filename):
        """
        Loads audit files to be used by python scripts.

        Args:
                filename (str): /path/to/audit/file.txt

        Returns:
                (list) List of lists. Each list has elements:
                        0 -- timestamp
                        1 -- duration
                        2 -- activity label (from variables.py)
        """
        Table = []
        with open(filename, "r") as File:
                for line in File:
                        if line != "\n":
                                Table.append(_floatify_list(line.rstrip("\n").lstrip("").split("\t")))
        Table = [x for x in Table if x != []]
        return Table

def indices_of_audit_starts_and_ends(loaded_audit_file):
        """
        Returns lists of indices (in loaded_audit_file) containing all SOAs and EOAs

        Args:
                loaded_audit_file (list): List of lists returned by load_audit_file .

        Returns:
                (tuple) (list, list): 2 Lists containing indices of all SOAs and EOAs respectively.

        Warns:
                UserWarning: If there are unequal numbers of SOAs and EOAs.
        """
        starts = [i for i,x in enumerate(loaded_audit_file) if x[2].split()[0] == "SOA"]
        ends   = [i for i,x in enumerate(loaded_audit_file) if x[2].split()[0] == "EOA"]
        if len(starts) != len(ends):
                warn("Unequal number of SOAs and EOAs")
        return starts, ends

def total_time_audited(loaded_audit_file):#DTS or MTS
        s, e = indices_of_audit_starts_and_ends(loaded_audit_file)
        tot_time = 0
        for i in range(len(s)):
                tot_time += loaded_audit_file[e[i]][0]-loaded_audit_file[s[i]][0]
        return tot_time
