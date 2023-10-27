# Thoughts

## Questions

Do I want a separate vlan for "lab" stuff versus "production" stuff?

## Groups

- servers - Common setup for servers
- desktops - Common setup for desktops
- desktop_alt - Desktop setting using my alternate/test desktop environment
- laptops - Extra settings for laptops
- htpc - Extra settings for Home Theatre PCs (HTPCs)
- moose_controller - MooseFS controller node
- moose_chunk - MooseFS chunck server (storage server)
- moose_meta - MooseFS meta logger & backup server
- k8_controller - Kubernetes controller node
- k8_worker - Kubernetes worker node
- proxmox
- media_collector - Extra settings for a torrent/newsfeed media collector & processor
- root_server - The "main"/"root" server with core services
- lab - Lab versions of something above
- prod - "Production" versions of something above

## Considerations

- TODO: Remove the ability to do standard apt installations in install_aps, they should use the builtin module for that
