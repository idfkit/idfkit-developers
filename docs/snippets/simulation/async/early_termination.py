from __future__ import annotations

from contextlib import aclosing

from idfkit.simulation import SimulationJob, async_simulate_batch_stream

jobs: list[SimulationJob] = ...  # type: ignore[assignment]


# --8<-- [start:example]
async def run_until_first_failure() -> None:
    async with aclosing(async_simulate_batch_stream(jobs, max_concurrent=4)) as stream:
        async for event in stream:
            if not event.result.success:
                print(f"Job {event.label} failed — aborting remaining")
                break
    # Leaving the block closed the stream, which cancelled the remaining jobs


# --8<-- [end:example]
