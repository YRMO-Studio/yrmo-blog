# YRMO Studio Blog

Repositorio público de contenido para el blog de [yrmostudio.com](https://yrmostudio.com).

Los artículos se almacenan como archivos JSON en `posts/` y se cargan dinámicamente en la web vía GitHub Raw API. No requiere rebuilds ni deploys de la web principal.

## Estructura

```
posts/
  index.json          # Índice de todos los artículos (orden cronológico inverso)
  2026-02-16-openclaw-openai.json   # Artículo individual
```

## Formato de artículo

```json
{
  "slug": "openclaw-openai",
  "title": "Título del artículo",
  "description": "Resumen corto para SEO y preview",
  "date": "2026-02-16",
  "author": "YRMO Studio",
  "tags": ["openclaw", "openai"],
  "readTime": "4 min",
  "body": "Contenido en markdown..."
}
```

## Pipeline

1. Cron diario busca noticias relevantes (OpenClaw, agentes autónomos, automatización)
2. Genera borrador como PR
3. Aprobación manual → merge
4. La web carga el contenido automáticamente (zero deploy)

## Seguridad

- Markdown renderizado con sanitización (no HTML crudo)
- No se ejecutan scripts del contenido
- PRs requieren aprobación manual
