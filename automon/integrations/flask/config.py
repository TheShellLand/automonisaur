# Javascript expression compatibility
def javascript_compatibility(app):
    jinja_options = app.jinja_options.copy()

    jinja_options.update(dict(
        block_start_string='<%',
        block_end_string='%>',
        variable_start_string='%%',
        variable_end_string='%%',
        comment_start_string='<#',
        comment_end_string='#>'
    ))

    return jinja_options
