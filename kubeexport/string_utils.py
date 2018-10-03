
class StringUtils(object):

    @staticmethod
    def get_first_row_which_starts_with(text, starts_with):
        rows = str(text).split("\n")
        for row in rows:
            str_row = str(row)
            if str_row.startswith(starts_with):
                return str_row

    @staticmethod
    def get_value_after_colon(text):
        if text is None:
            return None
        colon_index = text.find(':')
        if colon_index > -1:
            return text[colon_index+1:].strip()