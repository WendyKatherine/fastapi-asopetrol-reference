# ADR-001 — SQLAlchemy síncrono

- **Fecha:** 2026-11-23
- **Estado:** aceptada
- **Decide:** Wendy Gómez

## Contexto

El repositorio necesita una capa de persistencia para el primer corte vertical con base de datos. La decisión afecta al menos a cinco cosas: el engine, la sesión por petición, los tests, la forma de las funciones de caso de uso y el manejador de rutas de FastAPI.

Las dependencias instaladas por error traían `sqlalchemy[asyncio]` y `asyncpg`, mientras el diseño describía sync con `psycopg`. La contradicción no se resolvía sola: había que decidir antes de escribir el primer modelo.

## Decisión

Se usa **SQLAlchemy 2.0 en modo síncrono** con el driver `psycopg` 3.

## Consecuencias

**Positivas**

- Un solo modelo mental. La sesión es un objeto normal, no un contexto asíncrono repartido por cada función.
- Los tests se escriben sin plugins de asyncio y sin `await` en cada aserción.
- Las rutas de FastAPI pueden ser `def` en lugar de `async def`: FastAPI las ejecuta en un hilo aparte y el I/O bloqueante no detiene el bucle de eventos.
- El objetivo declarado del proyecto es **comprensión y criterio**, no concurrencia medida. Sync permite explicar cada línea.

**Negativas**

- Menor capacidad de conexiones concurrentes por proceso. Se mitiga con más procesos (gunicorn con workers de uvicorn), que es el modelo habitual en contenedores.
- Los casos de uso quedan atados a una firma síncrona. Migrar a async después obliga a tocar la capa de aplicación completa, no solo el repositorio.

**Costo de revertir**

Medio. Cambiar de sync a async implica: reemplazar el driver, reescribir la sesión como generador asíncrono, convertir los casos de uso en `async def`, ajustar los tests y añadir `pytest-asyncio`. Es una rama de un día, no un ajuste.

## Alternativas rechazadas

**Async desde el inicio (`asyncpg`).** Da mejor rendimiento bajo concurrencia alta, que este proyecto no va a medir ni necesitar. Añade `await` en cada capa y un modelo mental que compite con el de Clean Architecture en la misma sesión de aprendizaje.

**SQLModel.** Reduce el código repetido entre modelo y esquema, pero oculta la separación entre dominio y persistencia que el repositorio quiere demostrar, y su ciclo de vida depende de un único mantenedor.

**ORM ajeno a SQLAlchemy.** El mercado laboral pide SQLAlchemy. Elegir otra cosa reduciría la transferibilidad del repositorio, que es su propósito.

## Revisión

Se reevalúa si aparece un caso de uso con requisito de concurrencia medible, o si el despliegue en AWS muestra límite de conexiones con más procesos. En ese momento se abre un ADR nuevo que reemplace a este; este no se edita.
