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
    }
}

export default Api