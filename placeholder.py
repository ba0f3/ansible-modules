#!/usr/bin/python
def main():

    module = AnsibleModule(
        # not checking because of daisy chain to file module
        argument_spec = dict(
            src = dict(required=True),
            dest = dict(required=True),
            placeholder = dict(required=True),
            backup = dict(default=False, type='bool'),
            strip = dict(default=False, type='bool')
        ),
        add_file_common_args=True
    )

    changed = False
    src       = os.path.expanduser(module.params['src'])
    dest      = os.path.expanduser(module.params['dest'])
    placeholder    = module.params['placeholder']
    backup    = module.params['backup']
    strip     = module.params['strip']

    result = dict(src=src, dest=dest)
    if not os.path.exists(src):
        module.fail_json(msg="Source (%s) does not exist" % src)

    if os.path.isdir(src):
        module.fail_json(msg="Source (%s) is not a file" % src)

    if not os.path.exists(dest):
        module.fail_json(msg="Destination (%s) does not exist" % dest)

    if os.path.isdir(dest):
        module.fail_json(msg="Destination (%s) is not a file" % dest)

    src_hash = module.sha1(src)
    result['checksum'] = src_hash

    if src_hash != module.sha1(dest):
        if backup:
            result['backup_file'] = module.backup_local(dest)

        content = open(dest, 'r').read()

        if not content.find(placeholder):
            module.fail_json(msg="No placeholder found tobe replaced for: \"%s\"" % placeholder)

        source = open(src, 'r').read()
        if strip:
            source = source.rstrip()

        content = content.replace(placeholder, source)
        f = open(dest, 'w')
        f.write(content)
        f.close()

        changed = True

    # handle file permissions
    file_args = module.load_file_common_arguments(module.params)
    result['changed'] = module.set_fs_attributes_if_different(file_args, changed)

    # Mission complete
    result['msg'] = "OK"
    module.exit_json(**result)


from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
