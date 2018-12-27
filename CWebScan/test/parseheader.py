import re
from urllib.parse import unquote_to_bytes as _unquote


_option_header_start_mime_type = re.compile(r',\s*([^;,\s]+)([;,]\s*.+)?')

_option_header_piece_re = re.compile(r'''
    ;\s*
    (?P<key>
        "[^"\\]*(?:\\.[^"\\]*)*"  # quoted string
    |
        [^\s;,=*]+  # token
    )
    \s*
    (?:  # optionally followed by =value
        (?:  # equals sign, possibly with encoding
            \*\s*=\s*  # * indicates extended notation
            (?P<encoding>[^\s]+?)
            '(?P<language>[^\s]*?)'
        |
            =\s*  # basic notation
        )
        (?P<value>
            "[^"\\]*(?:\\.[^"\\]*)*"  # quoted string
        |
            [^;,]+  # token
        )?
    )?
    \s*
''', flags=re.VERBOSE)


def unquote_header_value(value, is_filename=False):
    r"""Unquotes a header value.  (Reversal of :func:`quote_header_value`).
    This does not use the real unquoting but what browsers are actually
    using for quoting.

    .. versionadded:: 0.5

    :param value: the header value to unquote.
    """
    if value and value[0] == value[-1] == '"':
        # this is not the real unquoting, but fixing this so that the
        # RFC is met will result in bugs with internet explorer and
        # probably some other browsers as well.  IE for example is
        # uploading files with "C:\foo\bar.txt" as filename
        value = value[1:-1]

        # if this is a filename and the starting characters look like
        # a UNC path, then just return the value without quotes.  Using the
        # replace sequence below on a UNC path has the effect of turning
        # the leading double slash into a single slash and then
        # _fix_ie_filename() doesn't work correctly.  See #458.
        if not is_filename or value[:2] != '\\\\':
            return value.replace('\\\\', '\\').replace('\\"', '"')
    return value

def parse_options_header(value, multiple=False):
    if not value:
        return '', {}

    result = []

    value = "," + value.replace("\n", ",")
    while value:
        match = _option_header_start_mime_type.match(value)
        if not match:
            break
        result.append(match.group(1))  # mimetype
        options = {}
        # Parse options
        rest = match.group(2)
        while rest:
            optmatch = _option_header_piece_re.match(rest)
            if not optmatch:
                break
            option, encoding, _, option_value = optmatch.groups()
            option = unquote_header_value(option)
            if option_value is not None:
                option_value = unquote_header_value(
                    option_value,
                    option == 'filename')
                if encoding is not None:
                    option_value = _unquote(option_value).decode(encoding)
            options[option] = option_value
            rest = rest[optmatch.end():]
        result.append(options)
        if multiple is False:
            return tuple(result)
        value = rest

    return tuple(result) if result else ('', {})

if __name__ == '__main__':
    # value = "multipart/form-data; boundary=----WebKitFormBoundary2dLrCE2AkRH48h2z; filename=dasdsad;"
    value = "application/x-www-form-urlencoded; charset=UTF-8"
    print(parse_options_header(value))