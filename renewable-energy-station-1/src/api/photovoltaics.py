# src/api/photovoltaics.py
from pathlib import Path
from flask import Blueprint, render_template
from src.models.photovoltaic_factory import PhotovoltaicFactory

bp = Blueprint("photovoltaics", __name__, url_prefix="/photovoltaics")

config_path = Path("/app/config/pv.json")
pv_factory = PhotovoltaicFactory(str(config_path))


@bp.route("/")
def list_pvs():
    try:
        available_pvs = pv_factory.get_available_pvs()
        print(f"Found PVs: {available_pvs}")  # Debug line
        return render_template(
            "photovoltaics.html",
            pvs=available_pvs,
            pv_factory=pv_factory,
        )
    except Exception as e:
        print(f"Error loading PVs: {e}")
        return render_template(
            "photovoltaics.html",
            pvs=[],
            pv_factory=pv_factory,
            error=str(e),
        )


@bp.route("/<pv_type>")
def pv_detail(pv_type):
    pv = pv_factory.create_pv(pv_type)
    return render_template("pv_detail.html", pv=pv, pv_type=pv_type)
