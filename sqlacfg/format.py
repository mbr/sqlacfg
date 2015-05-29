def _ini_value(val, comment_prefixes=('#', ';'), inline_comment_prefixes=None):
    if val is True:
        return 'yes'
    if val is False:
        return 'no'
    str_val = str(val)
    str_val.strip().replace('\n', r'\n').replace('\r', r'\r')

    for prefix in comment_prefixes:
        if str_val.startswith(prefix):
            raise ValueError('Escaping a comment prefix is not supported')

    for prefix in inline_comment_prefixes:
        if prefix in str_val:
            raise ValueError('Escaping a comment prefix is not supported')

    return str_val


def ini_format(cfg):
    sections = []
    for name, sect in sorted(cfg.items()):
        sect_values = ('{} = {}'.format(key, value)
                       for key, value in sorted(sect.iteritems()))
        sections.append(u'[{}]\n{}\n'.format(
            name, '\n'.join(sect_values)
        ))

    return '\n'.join(sections)
