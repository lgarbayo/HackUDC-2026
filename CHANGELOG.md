# Changelog

Todos los cambios notables en MeigaSearch serán documentados en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto sigue [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Soporte para búsqueda por rango de fechas (between)
- Integración de múltiples proveedores de LLM
- Dashboard de analytics para documentos indexados
- Soporte para búsqueda en imágenes con CLIP

## [1.0.0] - 2026-03-01

### Initial Hackathon Release

#### Added
- ✨ **Ingesta Mágica**: Soporta PDF, XLSX, CSV, TXT, PNG, JPG con OCR automático
- 🔍 **Búsqueda Híbrida**: Búsqueda semántica + léxica en paralelo, sin APIs externas
- 🤖 **Copiloto RAG**: Expansión automática de queries con LLM local (Qwen/SmolLM)
- 📁 **Filtros Avanzados**: Filtrar por mes, año, autor, categoría, tipo de archivo
- 🛡️ **Autenticación JWT**: Control de acceso con RBAC por departamento
- 📊 **Extracción de Metadatos**: ExifTool para extraer automáticamente titulares, autores, fechas
- ⚡ **Procesamiento Async**: Celery + Redis para indexación no bloqueante
- 🗂️ **Base de datos vectorial**: Qdrant para búsqueda rápida de embeddings
- 🎨 **UI Responsive**: Frontend vanilla JS, funcionaldad en móvil y desktop
- 📈 **Performance**: Búsqueda en <500ms para 1000+ documentos
- 🔐 **Sin dependencias en cloud**: Toda la IA corre localmente

#### Features
- Búsqueda directa y modo de búsqueda descriptiva (LLM-assisted)
- Historial de búsquedas con localStorage
- Configuración de proveedor LLM (local/openai)
- API RESTful completa con documentación Swagger
- Debug endpoints para diagnosticar metadatos
- Health checks detallados

#### Documentation
- README con guía de instalación y uso
- CONTRIBUTING.md con estándares de código
- CODE_OF_CONDUCT.md basado en Contributor Covenant
- SECURITY.md con política de vulnerabilidades
- Docstrings en funciones principales

#### Infrastructure
- Docker Compose con Qdrant + Redis + FastAPI + Celery
- Scripts de inicialización de base de datos
- Soporte para desarrollo con hot-reload
- Logs detallados en todas las operaciones

---

## Formato de versiones futuras

### [X.Y.Z] - YYYY-MM-DD

#### Added
- Nuevas features

#### Changed
- Cambios en features existentes

#### Deprecated
- Features que serán removidas próximamente

#### Removed
- Features removidas

#### Fixed
- Bugs arreglados

#### Security
- Vulnerabilidades reportadas
