import perms_tools

def confirm_action(confirmation_message, cancelation_message, action):
    if input(f'{confirmation_message} [y/n] ').lower() in ('o', 'y'):
        action()
    else:
        print(cancelation_message)


# ---- commands definitions
def export_perms(src_directory, permission_save_file):
    perms_tools.perm_export(src_directory, permission_save_file)


def import_perms(dst_directory, permission_save_file):
    patch = perms_tools.perm_import(dst_directory, permission_save_file)
    print(patch)
    confirm_action("Proceed ?", "nothing done", lambda: patch.apply())


def auto_perms(directory):
    patch = perms_tools.perm_auto_patch(directory)
    print(patch)
    confirm_action("Proceed ?", "nothing done", lambda: patch.apply())
