"""Environment loading and dual-export for Genblaze B2 + NVIDIA NIM."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parent.parent


def resolve_repo_root(app_dir: Path = APP_DIR) -> Path:
    """Locate monorepo root when present; otherwise the app dir (Docker image).

    Local layout: ``<repo>/mrs/apps/genblaze-media`` → parents[2] is repo root.
    Docker layout: app lives at ``/app`` with no monorepo parents — use ``app_dir``.
    """
    try:
        candidate = app_dir.parents[2]
    except IndexError:
        return app_dir
    if (candidate / "mrs" / "apps" / "genblaze-media").is_dir():
        return candidate
    if (candidate / ".git").exists():
        return candidate
    return app_dir


REPO_ROOT = resolve_repo_root()


def _resolve_renderer_core_script(
    name: str,
    repo_root: Path = REPO_ROOT,
    app_dir: Path = APP_DIR,
) -> Path:
    """Resolve a renderer-core ``scripts/<name>`` file across known layouts.

    Two layouts are supported without operators setting an env override:

    * Monorepo checkout — ``<repo>/mrs/packages/renderer-core/scripts/<name>``.
    * Repo-root Docker image — the Dockerfile copies ``renderer-core`` to
      ``/app/renderer-core``, so the file lives at
      ``<app_dir>/renderer-core/scripts/<name>`` (``app_dir`` is ``/app``).

    The first existing candidate wins. When neither exists (e.g. the app-only
    Docker image that bundles no renderer-core), the monorepo path is returned
    so callers still surface a canonical location in errors and ``/health``
    reports ``script_found: false`` rather than crashing.
    """
    monorepo = (
        repo_root / "mrs" / "packages" / "renderer-core" / "scripts" / name
    )
    if monorepo.is_file():
        return monorepo
    docker = app_dir / "renderer-core" / "scripts" / name
    if docker.is_file():
        return docker
    return monorepo


def rt4d_default_script_path(repo_root: Path = REPO_ROOT) -> Path:
    """Default path to the renderer-core render-still CLI.

    Resolves the monorepo checkout path first, then the repo-root Docker image
    layout (``/app/renderer-core/scripts/render-still.mjs``). In the app-only
    Docker image neither exists; the provider treats a missing script (or
    missing node) as ``rt4d_available = False`` and the ``/health`` endpoint
    reports it, rather than raising at import time.
    """
    return _resolve_renderer_core_script("render-still.mjs", repo_root)


def scene_spec_default_script_path(repo_root: Path = REPO_ROOT) -> Path:
    """Default path to the SceneSpecification render-scene CLI.

    Docker-layout aware (see :func:`_resolve_renderer_core_script`) so the
    repo-root image resolves ``/app/renderer-core/scripts/render-scene.mjs``
    without requiring ``SCENE_SPEC_SCRIPT_PATH``.
    """
    return _resolve_renderer_core_script("render-scene.mjs", repo_root)


def validate_scene_spec_default_script_path(repo_root: Path = REPO_ROOT) -> Path:
    """Default path to SceneSpecification capability validator (Node SoT).

    Docker-layout aware so the repo-root image resolves
    ``/app/renderer-core/scripts/validate-scene-spec.mjs`` without requiring
    ``VALIDATE_SCENE_SPEC_SCRIPT_PATH``.
    """
    return _resolve_renderer_core_script("validate-scene-spec.mjs", repo_root)


def _load_dotenv_files() -> list[str]:
    """Load repo-root `.env` then app-local `.env` without clobbering process env.

    Uses override=False so deploy-host / test monkeypatches win over file values.
    On Render, secrets come from the dashboard env — dotenv files are optional.
    """
    loaded: list[str] = []
    seen: set[Path] = set()
    for path in (REPO_ROOT / ".env", APP_DIR / ".env"):
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if path.is_file():
            load_dotenv(path, override=False)
            loaded.append(str(path))
    return loaded


def dual_export_b2_keys() -> None:
    """Genblaze-s3 reads B2_APP_KEY; MRS docs use B2_APPLICATION_KEY. Bridge both."""
    app_key = (os.getenv("B2_APP_KEY") or os.getenv("B2_APPLICATION_KEY") or "").strip()
    if app_key:
        os.environ["B2_APP_KEY"] = app_key
        # Keep APPLICATION_KEY set for @mrs/storage-b2 / npm scripts in same shell.
        if not (os.getenv("B2_APPLICATION_KEY") or "").strip():
            os.environ["B2_APPLICATION_KEY"] = app_key


def dual_export_nvidia_keys() -> None:
    """Bridge NVIDIA_API_KEY with NGC_API_KEY / NVIDIA_NIM_API_KEY aliases."""
    key = (
        os.getenv("NVIDIA_API_KEY")
        or os.getenv("NGC_API_KEY")
        or os.getenv("NVIDIA_NIM_API_KEY")
        or ""
    ).strip()
    if not key:
        return
    os.environ["NVIDIA_API_KEY"] = key
    if not (os.getenv("NGC_API_KEY") or "").strip():
        os.environ["NGC_API_KEY"] = key
    if not (os.getenv("NVIDIA_NIM_API_KEY") or "").strip():
        os.environ["NVIDIA_NIM_API_KEY"] = key


@dataclass(frozen=True)
class Settings:
    """Runtime settings (names only; values come from env)."""

    nvidia_api_key: str | None
    fal_api_key: str | None
    b2_key_id: str | None
    b2_app_key: str | None
    b2_bucket: str
    b2_region: str
    b2_endpoint: str | None
    storage_prefix: str
    image_model: str
    video_model: str
    video_enabled: bool
    video_backend: str
    seedance_model: str
    seedance_resolution: str
    seedance_duration: str
    seedance_aspect_ratio: str
    seedance_generate_audio: bool
    seedance_watermark: bool | None
    embed_model: str
    embed_url: str
    embed_timeout_seconds: float
    store_full_embeddings: bool
    presign_expires_seconds: int
    dry_run: bool
    b2_probe_on_health: bool
    abstract_retry_on_blank: bool
    empty_504_retry: bool
    empty_504_retry_delay_seconds: float
    nvidia_warmup_on_startup: bool
    dotenv_loaded: tuple[str, ...]
    # --- RT4D deterministic renderer backend (defaults keep NVIDIA the default) ---
    image_backend: str = "nvidia"
    image_fallback_to_rt4d: bool = False
    # --- Local Lemonade (AMD) OpenAI-compatible image API ---
    lemonade_base_url: str = "http://127.0.0.1:13305/api/v1"
    lemonade_model: str | None = None
    lemonade_size: str = "512x512"
    lemonade_steps: int = 4
    lemonade_timeout_seconds: float = 600.0
    lemonade_api_key: str | None = None
    # GENBLAZE_SKIP_LOCAL_SD=1 — skip Lemonade/local SD (AMD hosts without sd-server).
    # Pre-render beauty on a cloud-capable / GMI-credit host instead.
    skip_local_sd: bool = False
    rt4d_node_path: str = "node"
    rt4d_script_path: str | None = None
    scene_spec_script_path: str | None = None
    # Final profile defaults match free-tier render.yaml pins so an unsynced
    # deploy cannot silently fall back to the old 448×448 / 20-sample path.
    rt4d_width: int = 256
    rt4d_height: int = 256
    rt4d_samples: int = 8
    rt4d_max_depth: int = 5
    rt4d_timeout_seconds: float = 180.0
    # When False (default), /api/generate stills also hard-clamp above the
    # deploy-safe ceiling even if RT4D_* env is mis-set higher.
    rt4d_allow_heavy: bool = False
    # Scene-spec render quality: "draft" (hackathon default — smaller/noisier,
    # renders in ~tens of seconds on CPU) or "final" (RT4D_* profile above).
    render_quality_default: str = "draft"
    rt4d_draft_width: int = 256
    rt4d_draft_height: int = 256
    rt4d_draft_samples: int = 4
    rt4d_draft_max_depth: int = 3
    # Image → SceneSpecification (NIM vision + heuristic fallback)
    image_to_scene_model: str = "meta/llama-3.2-11b-vision-instruct"
    image_to_scene_chat_url: str = "https://integrate.api.nvidia.com/v1/chat/completions"
    image_to_scene_timeout_seconds: float = 120.0
    validate_scene_spec_script_path: str | None = None
    flux_then_scene: bool = False
    # --- Image polish (img2img diffusion cleanup) ---
    polish_enabled: bool = False
    polish_model: str | None = None
    polish_default_strength: float = 0.45
    polish_backend: str = "auto"
    # Keyless HF Space img2img backend (FLUX.2-Klein-9B ZeroGPU Space)
    hfspace_url: str = "https://m3st3rj4k3l-flux-2-klein-multi-lora.hf.space"
    hfspace_timeout_seconds: float = 180.0
    # --- GMI Cloud (GenBlaze SDK fan-out; hackathon credits) ---
    gmi_api_key: str | None = None
    gmi_base_url: str | None = None
    gmi_image_model: str = "seedream-5.0-lite"
    # --- Demo cache (pre-render → B2 → live overlay) ---
    # GENBLAZE_DEMO_CACHE=1 serves B2 cached frames; still probes provider health.
    demo_cache_enabled: bool = False
    demo_cache_shot_id: str | None = None
    demo_cache_default_frame: int = 0
    # GENBLAZE_PRE_RENDER_FALLBACK=1 — on live generate failure, serve
    # {prefix}/pre-render/structure.png from B2 (source=b2-structure-cache).
    pre_render_fallback_enabled: bool = False
    pre_render_shots_per_hour: int = 4
    # --- Media look lane (FLUX/Lemonade/polish prompt steer; partial) ---
    # GENBLAZE_STYLE=anime | default. Request body ``style`` overrides.
    media_style: str = "default"
    # --- Prompt → SceneSpecification / Engine3DWorldDocument (out-of-process) ---
    prompt_scene_bridge_enabled: bool = True
    prompt_scene_bridge_script_path: str | None = None
    prompt_scene_bridge_python: str | None = None
    prompt_scene_infinity_src: str | None = None
    prompt_scene_bridge_timeout_seconds: float = 90.0
    # Opt-in: expand Engine3D generator stub via engine3d-core Node CLI
    prompt_scene_expand_world: bool = False
    # --- Engine3D structure still (soft-raster beauty+AOVs) ---
    engine3d_still_enabled: bool = True
    engine3d_still_script_path: str | None = None
    engine3d_still_timeout_seconds: float = 120.0
    worlddocument_rt4d_script_path: str | None = None
    # --- Proton soft-splat (six-mod; default OFF) ---
    proton_raster_enabled: bool = False
    proton_raster_script_path: str | None = None
    proton_raster_timeout_seconds: float = 120.0
    # --- Engine3D short cinematic sequence (soft-raster orbit) ---
    engine3d_sequence_enabled: bool = True
    engine3d_sequence_script_path: str | None = None
    engine3d_sequence_timeout_seconds: float = 180.0
    engine3d_sequence_max_frames: int = 24
    # --- Face Creation Assist (Sovereign X Node CLI; default OFF) ---
    face_creation_assist_enabled: bool = False
    face_creation_assist_cli_path: str | None = None
    face_creation_assist_timeout_seconds: float = 120.0
    # --- BYOK (session key from browser; hosted off unless flag) ---
    # GENBLAZE_ALLOW_BYOK=1 enables per-request keys on non-loopback / Render.
    # Default False: local loopback still accepts BYOK; hosted rejects.
    allow_byok: bool = False
    # --- ChatGPT / Custom GPT plugin ---
    chatgpt_plugin_key: str | None = None
    public_base_url: str | None = None
    cors_allow_all: bool = False

    @property
    def nvidia_configured(self) -> bool:
        return bool(self.nvidia_api_key)

    @property
    def seedance_configured(self) -> bool:
        return bool(self.fal_api_key)

    @property
    def b2_configured(self) -> bool:
        return bool(self.b2_key_id and self.b2_app_key and self.b2_bucket)

    @property
    def video_available(self) -> bool:
        """Operator can attempt video (flag on + backend credentials, or dry-run)."""
        if not self.video_enabled:
            return False
        if self.dry_run:
            return True
        if self.video_backend == "seedance":
            return self.seedance_configured
        return self.nvidia_configured


def get_settings() -> Settings:
    loaded = _load_dotenv_files()
    dual_export_b2_keys()
    dual_export_nvidia_keys()

    region = (os.getenv("B2_REGION") or "us-east-005").strip()
    endpoint = (os.getenv("B2_ENDPOINT") or "").strip() or None
    if not endpoint and region:
        endpoint = f"https://s3.{region}.backblazeb2.com"

    dry = (os.getenv("GENBLAZE_DRY_RUN") or "").strip().lower() in {"1", "true", "yes"}
    store_full = (os.getenv("NVIDIA_STORE_FULL_EMBEDDINGS") or "1").strip().lower() in {
        "1",
        "true",
        "yes",
    }
    # Default OFF: /health ListObjects is a Class C burn (Render probes + UI loads).
    # Opt in with B2_PROBE_ON_HEALTH=1 only when debugging credentials.
    b2_probe = (os.getenv("B2_PROBE_ON_HEALTH") or "").strip().lower() in {
        "1",
        "true",
        "yes",
    }
    # Default ON: one FLUX retry with abstract rewrite after near-black people blanks.
    # Set GENBLAZE_ABSTRACT_RETRY=0 to save NIM/B2 Class C when over free-tier caps.
    abstract_retry = (os.getenv("GENBLAZE_ABSTRACT_RETRY") or "1").strip().lower() not in {
        "0",
        "false",
        "no",
        "off",
    }
    # Default OFF: judge/demo path is FLUX stills. Cosmos video stays an
    # operator opt-in (GENBLAZE_VIDEO_ENABLED=1) when the key's catalog is live.
    video_enabled = (os.getenv("GENBLAZE_VIDEO_ENABLED") or "0").strip().lower() not in {
        "0",
        "false",
        "no",
        "off",
    }
    backend_raw = (os.getenv("GENBLAZE_VIDEO_BACKEND") or "nvidia").strip().lower()
    video_backend = "seedance" if backend_raw in {"seedance", "fal", "bytedance"} else "nvidia"
    fal_key = (
        os.getenv("FAL_KEY") or os.getenv("SEEDANCE_API_KEY") or os.getenv("FAL_API_KEY") or ""
    ).strip() or None
    seedance_audio = (os.getenv("SEEDANCE_GENERATE_AUDIO") or "1").strip().lower() not in {
        "0",
        "false",
        "no",
        "off",
    }
    wm_raw = (os.getenv("SEEDANCE_WATERMARK") or "0").strip().lower()
    if wm_raw in {"", "default", "omit"}:
        seedance_watermark: bool | None = None
    else:
        seedance_watermark = wm_raw not in {"0", "false", "no", "off"}

    return Settings(
        nvidia_api_key=(
            os.getenv("NVIDIA_API_KEY")
            or os.getenv("NGC_API_KEY")
            or os.getenv("NVIDIA_NIM_API_KEY")
            or ""
        ).strip()
        or None,
        fal_api_key=fal_key,
        b2_key_id=(os.getenv("B2_KEY_ID") or os.getenv("AWS_ACCESS_KEY_ID") or "").strip()
        or None,
        b2_app_key=(os.getenv("B2_APP_KEY") or os.getenv("B2_APPLICATION_KEY") or "").strip()
        or None,
        b2_bucket=(os.getenv("B2_BUCKET") or "Mandala-Rendering-System").strip(),
        b2_region=region,
        b2_endpoint=endpoint,
        storage_prefix=(os.getenv("GENBLAZE_STORAGE_PREFIX") or "genblaze-media").strip(),
        image_model=(
            os.getenv("GENBLAZE_IMAGE_MODEL") or "black-forest-labs/flux.1-schnell"
        ).strip(),
        video_model=(
            os.getenv("GENBLAZE_VIDEO_MODEL")
            # Upstream-valid default; operators can fall back to the 12b
            # Cosmos 1.0 slug when it is available on their NVIDIA key.
            or "nvidia/cosmos-1.0-7b-diffusion-text2world"
        ).strip(),
        video_enabled=video_enabled,
        video_backend=video_backend,
        seedance_model=(
            os.getenv("SEEDANCE_MODEL") or "bytedance/seedance-2.0/text-to-video"
        ).strip(),
        seedance_resolution=(os.getenv("SEEDANCE_RESOLUTION") or "720p").strip(),
        seedance_duration=(os.getenv("SEEDANCE_DURATION") or "5").strip(),
        seedance_aspect_ratio=(os.getenv("SEEDANCE_ASPECT_RATIO") or "16:9").strip(),
        seedance_generate_audio=seedance_audio,
        seedance_watermark=False if seedance_watermark is None else seedance_watermark,
        embed_model=(
            os.getenv("NVIDIA_EMBED_MODEL") or "nvidia/nv-embedcode-7b-v1"
        ).strip(),
        embed_url=(
            os.getenv("NVIDIA_EMBED_URL")
            or "https://integrate.api.nvidia.com/v1/embeddings"
        ).strip(),
        embed_timeout_seconds=float(os.getenv("NVIDIA_EMBED_TIMEOUT") or "60"),
        store_full_embeddings=store_full,
        presign_expires_seconds=int(os.getenv("GENBLAZE_PRESIGN_EXPIRES") or "3600"),
        dry_run=dry,
        b2_probe_on_health=b2_probe,
        abstract_retry_on_blank=abstract_retry,
        empty_504_retry=empty_504_retry,
        empty_504_retry_delay_seconds=empty_504_delay,
        nvidia_warmup_on_startup=nvidia_warmup,
        dotenv_loaded=tuple(loaded),
        image_backend=image_backend,
        image_fallback_to_rt4d=image_fallback_to_rt4d,
        lemonade_base_url=lemonade_base_url,
        lemonade_model=lemonade_model,
        lemonade_size=lemonade_size,
        lemonade_steps=lemonade_steps,
        lemonade_timeout_seconds=lemonade_timeout,
        lemonade_api_key=lemonade_api_key,
        skip_local_sd=skip_local_sd,
        rt4d_node_path=rt4d_node_path,
        rt4d_script_path=rt4d_script_override,
        scene_spec_script_path=scene_spec_script_override,
        rt4d_width=rt4d_width,
        rt4d_height=rt4d_height,
        rt4d_samples=rt4d_samples,
        rt4d_max_depth=rt4d_max_depth,
        rt4d_timeout_seconds=rt4d_timeout,
        rt4d_allow_heavy=rt4d_allow_heavy,
        render_quality_default=render_quality_default,
        rt4d_draft_width=rt4d_draft_width,
        rt4d_draft_height=rt4d_draft_height,
        rt4d_draft_samples=rt4d_draft_samples,
        rt4d_draft_max_depth=rt4d_draft_max_depth,
        image_to_scene_model=image_to_scene_model,
        image_to_scene_chat_url=image_to_scene_chat_url,
        image_to_scene_timeout_seconds=image_to_scene_timeout,
        validate_scene_spec_script_path=validate_scene_spec_override,
        flux_then_scene=flux_then_scene,
        polish_enabled=polish_enabled,
        polish_model=polish_model,
        polish_default_strength=polish_strength,
        polish_backend=polish_backend,
        hfspace_url=hfspace_url,
        hfspace_timeout_seconds=hfspace_timeout,
        gmi_api_key=gmi_api_key,
        gmi_base_url=gmi_base_url,
        gmi_image_model=gmi_image_model,
        demo_cache_enabled=demo_cache_enabled,
        demo_cache_shot_id=demo_cache_shot_id,
        demo_cache_default_frame=demo_cache_default_frame,
        pre_render_fallback_enabled=pre_render_fallback_enabled,
        pre_render_shots_per_hour=pre_render_shots_per_hour,
        media_style=media_style,
        prompt_scene_bridge_enabled=prompt_scene_bridge_enabled,
        prompt_scene_bridge_script_path=prompt_scene_bridge_script_override,
        prompt_scene_bridge_python=prompt_scene_bridge_python,
        prompt_scene_infinity_src=prompt_scene_infinity_src,
        prompt_scene_bridge_timeout_seconds=prompt_scene_bridge_timeout,
        prompt_scene_expand_world=prompt_scene_expand_world,
        engine3d_still_enabled=engine3d_still_enabled,
        engine3d_still_script_path=engine3d_still_script_override,
        engine3d_still_timeout_seconds=engine3d_still_timeout,
        worlddocument_rt4d_script_path=worlddocument_rt4d_script_override,
        proton_raster_enabled=proton_raster_enabled,
        proton_raster_script_path=proton_raster_script_override,
        proton_raster_timeout_seconds=proton_raster_timeout,
        engine3d_sequence_enabled=engine3d_sequence_enabled,
        engine3d_sequence_script_path=engine3d_sequence_script_override,
        engine3d_sequence_timeout_seconds=engine3d_sequence_timeout,
        engine3d_sequence_max_frames=engine3d_sequence_max_frames,
        face_creation_assist_enabled=face_creation_assist_enabled,
        face_creation_assist_cli_path=face_creation_assist_cli_path,
        face_creation_assist_timeout_seconds=face_creation_assist_timeout,
        allow_byok=allow_byok,
        chatgpt_plugin_key=chatgpt_plugin_key,
        public_base_url=public_base_url,
        cors_allow_all=cors_allow_all,
    )


NVIDIA_SETUP_HELP = (
    "NVIDIA_API_KEY is missing. Create a free nvapi- key at "
    "https://build.nvidia.com/ and set NVIDIA_API_KEY in the repo-root .env "
    "(or the deploy host env). Live generate requires this key; "
    "GENBLAZE_DRY_RUN=1 is for unit tests only."
)

SEEDANCE_SETUP_HELP = (
    "Seedance backend selected but FAL_KEY / SEEDANCE_API_KEY is missing. "
    "Create a key at https://fal.ai/dashboard/keys and set FAL_KEY "
    "(see env.seedance.example). fal API usage is billed; consumer Dreamina/"
    "Jimeng free credits are not this API. GENBLAZE_DRY_RUN=1 skips live calls."
)
