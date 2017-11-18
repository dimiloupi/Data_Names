# regular expressions for reading namesdb.txt file
import re
# for sys.exit()
import sys

# for sorting tuples based on element 1
def get_key_1(item):
    return item[1]

class Babies:
    # the constructor takes a filename as an argument
    def __init__(self, filename):
        # initializes main members
        self.babynames = []
        self.origins = {}
        self.babynames = self.read_names_from_file(filename)

    # helper function for reading file and handling exceptions (file does not exist, can not be opened etc)
    def try_open_file(self, filename, attr='r'):
        try:
            f = open(filename, attr)
            return (True, f)
        except IOError:
            print "Error opening file: ", filename
            return (False, 0)

    # method for reading a file
    def read_names_from_file(self, filename):
        # initialize return data
        data = []
        # open the file
        (file_ok, f) = self.try_open_file(filename, 'r')
        if file_ok:
            # variable used to return error if a line is malformatted
            line_cnt = 1
            for line in f:
                # get rid of trailing spaces/newline character
                line = line.strip()
                # split the two columns
                data_cur = line.split()
                # check proper input data format
                if (len(data_cur) < 2) or ((data_cur[1] != "BOY") and (data_cur[1] != "GIRL")):
                    print "Malformatted data at line ", line_cnt, " of file: ", filename
                    print "Line: ", line
                else:
                    # append to results, only if valid
                    data.append(data_cur)
                line_cnt += 1
            if len(data) == 0:
                print "No records found in file: ", filename
            # close the file
            f.close()

        return data

    # helper function to check whether babynames are loaded properly
    def check_valid_babynames(self):
        if (self.babynames is None) or (len(self.babynames) == 0):
            return False
        else:
            return True
    # helper function to check whether origins are loaded properly
    def check_valid_origins(self):
        if (self.origins is None) or (self.origins == {}):
            return False
        else:
            return True

    # Gets total number of births for a specific (or any) gender
    def get_total_births(self, gender=None):
        if self.check_valid_babynames:
            if (gender is None):
                # no need to traverse the list and check for genres, just get its length
                return len(self.babynames)
            else:
                # initialize counter
                count = 0
                # traverse the list, increase counter on specific gender
                for rec in self.babynames:
                    if (rec[1] == gender):
                        count += 1
                return count
        else:
            # avoid crashing if no records are loaded (maybe a corrupt file?)
            return 0

    # returns names beginning with first_char character
    def get_names_beginning_with(self, first_char, gender=None):
        # initialize list
        sorted_l = []
        # traverse list, append matched records
        for rec in self.babynames:
            if (rec[0][0] == first_char) and ( (gender is None) or (rec[1] == gender) ):
                sorted_l.append(rec[0])
        # sort list and return
        sorted_l = sorted(sorted_l)
        return sorted_l

    # returns top N most frequent names
    def get_top_N(self, N, gender=None):
        # use dictionary for occurence counting for each name
        names_d = {}
        for rec in self.babynames:
            if (gender is None) or (rec[1] == gender):
                # check if the key already exists
                if names_d.has_key(rec[0]):
                    # if it exists, increment number of occurences
                    names_d[rec[0]] = names_d[rec[0]] + 1
                else:
                    # if it doesn't exist, initialize to 1 (1st occurence of the name)
                    names_d[rec[0]] = 1
        # convert result to tuple...
        names_t = names_d.items()
        # ...and sort it based on 2nd element
        names_t.sort(key=get_key_1, reverse=True)
        return names_t[0:N]

    # returns ratio of specific-gender babies to total babies
    def get_gender_ratio(self, gender):
        gender_cnt = 0.0
        for rec in self.babynames:
            if (rec[1] == gender):
                gender_cnt += 1
        return gender_cnt / len(self.babynames)

    def read_origins_from_file(self, origins_filename):
        # initialize return data
        self.origins = {}
        # open the file
        (file_ok, f) = self.try_open_file(origins_filename, 'r')
        if file_ok:
            for line in f:
                # get rid of trailing spaces/newline character
                line = line.strip()
                # matched regular expression is:
                # [Start of line][Non-newline characters][3 spaces (   )][F or M][whitespace chars][Non-comma (,)][, (comma)][one space( )][Non-newline characters][end of line]
                matched = re.search('^([^\n]+)   ([FM])\s+([^,]+), ([^\n]+)$', line)
                if len(matched.groups()) != 4:
                    print "Malformatted origins file"
                else:
                    # the same name can be both Male and Female
                    # so we can't just use the name, but a combination of Name-Gender
                    key_t = (matched.groups()[0], matched.groups()[1])
                    # value is origin + name meaning
                    value_t = (matched.groups()[2], matched.groups()[3])
                    # CAUTION! IF there is a douplicate record (same Name-Gender combination) in the origins file,
                    # behavior is: ignore the 2nd - take only the 1st occurence into account
                    if not(self.origins.has_key(key_t)):
                        self.origins[key_t] = value_t
            f.close()

    # helper function that returns a dictionary of {origin, count}
    def get_origins_cnt_dict(self):
        origins_cnt = {}
        for rec in self.babynames:
            # get the gender in M/F format, according to origins file
            if rec[1] == "GIRL":
                gender = "F"
            else:
                gender = "M"
            # look for a combination of Name-Gender
            key_name = (rec[0], gender)

            # first look in the origins read from file
            if self.origins.has_key(key_name):
                # key found, now look for that key in the counter
                key_origin = self.origins[key_name][0]
                if (origins_cnt.has_key(key_origin)):
                    # key found in counter, increment it
                    origins_cnt[key_origin] = origins_cnt[key_origin] + 1
                else:
                    # key not there yet, initializes
                    origins_cnt[key_origin] = 1
        return origins_cnt

    # actual function that returns the list of origin-count tuples
    def get_origin_counts(self):
        # check first that everything is loaded properly
        if self.check_valid_babynames() and self.check_valid_origins():
            # first convert dictionary to tuple and then sort
            origins_cnt_t = self.get_origins_cnt_dict().items()
            origins_cnt_t.sort(key=get_key_1, reverse=True)
            return origins_cnt_t
        else:
            # print errors and return empty list
            print "You need to load valid babynames & origins files first."
            print " -> Babynames: ", "OK" if self.check_valid_babynames() else "Missing!"
            print " -> Origins:   ", "OK" if self.check_valid_origins() else "Missing!"
            return []
