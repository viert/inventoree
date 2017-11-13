const Api = {
    Hosts: {
        EditorFields: [
            'fqdn',
            'description',
            'datacenter',
            'group',
            'datacenter_id',
            'group_id',
            'tags',
            'custom_fields',
        ],
        ViewFields: [
            '_id',
            'fqdn',
            'description',
            'datacenter',
            'group',
            'group_id',
            'tags',
            'custom_fields',
            'all_tags',
            'all_custom_fields',
            'modification_allowed'
        ],
        ListFields: [
            '_id',
            'fqdn',
            'group',
            'datacenter_name',
            'description',
            'all_tags',
            'all_custom_fields',
            'modification_allowed',
        ]
    },
    Groups: {
        EditorFields: [
            '_id',
            'children',
            'name',
            'description',
            'project',
            'tags',
            'custom_fields',
            'hosts'
        ],
        ViewFields: [
            '_id',
            'name',
            'description',
            'children',
            'parents',
            'hosts',
            'tags',
            'custom_fields',
            'all_tags',
            'all_custom_fields',
            'project',
            'modification_allowed'
        ],
        ListFields: [
            '_id',
            'name',
            'description',
            'all_tags',
            'all_custom_fields',
            'project',
            'modification_allowed'
        ]
    },
    Projects: {
        EditorFields: [
            '_id',
            'name',
            'description',
            'email',
            'root_email',
            'members'
        ],
        ViewFields: [
            '_id',
            'name',
            'email',
            'owner',
            'members',
            'root_email',
            'description',
            'groups_count',
            'modification_allowed'
        ],
        ListFields: [
            '_id',
            'name',
            'root_email',
            'email',
            'owner',
            'description',
            'modification_allowed'
        ]
    },
    Datacenters: {
        ViewFields: [
            '_id',
            'name',
            'human_readable',
            'parent',
            'root',
            'children'
        ]
    },
    Users: {
        EditorFields: [
            '_id',
            'username',
            'first_name',
            'last_name',
            'email',
            'supervisor',
            'supervisor_set_allowed',
            'modification_allowed'
        ],
        ListFields: [
            '_id',
            'username',
            'first_name',
            'last_name',
            'email',
            'supervisor',
            'modification_allowed'
        ],
        ViewFields: [
            '_id',
            'username',
            'first_name',
            'last_name',
            'email',
            'supervisor',
            'modification_allowed',
            'projects_owned',
            'projects_included_into'
        ]
    }
}

export default Api