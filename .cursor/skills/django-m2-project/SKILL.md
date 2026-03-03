---
name: django-m2-project
description: Django M2 backend conventions for clean architecture, DRF, serializers, CBV, Black, flake8, hardcoding, Swagger. Use when adding endpoints, serializers, views, or modifying API structure.
---

# Django M2 Project

## Quick Reference

- **Architecture**: Clean separation — helpers, serializers, API endpoints in separate folders
- **Serializers**: One request + one response per endpoint; organized in `serializers/<endpoint>/`
- **Views**: Class-based only; mixins allowed
- **Formatting**: Black + flake8
- **Config**: Hardcode everything; use config package for explicit values
- **Docs**: Update Swagger when endpoints change

## Adding a New Endpoint

1. Create `serializers/<endpoint_name>/request.py` and `response.py`
2. Create view in `api/v1/<endpoint_name>/views.py` (CBV)
3. Wire URL in app's `urls.py`
4. Update Swagger documentation

## Structure Checklist

- [ ] Request serializer in `serializers/<endpoint>/request.py`
- [ ] Response serializer in `serializers/<endpoint>/response.py`
- [ ] View in `api/v1/<endpoint>/views.py` (CBV)
- [ ] Shared enums/types in `core` or `shared` package
- [ ] Swagger updated after changes
