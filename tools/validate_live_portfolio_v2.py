from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAP=ROOT/"architecture"/"DISCOVERY_LIVE_PORTFOLIO_MAP_V2.json"
def validate():
    d=json.loads(MAP.read_text(encoding="utf-8")); rows=d["repositories"]; names=[r["repository"] for r in rows]
    assert d["schema"]=="DISCOVERY_LIVE_PORTFOLIO_MAP_V2"
    assert len(rows)==59 and len(set(names))==59
    assert d["counts"]=={"total":59,"bound_conditional":41,"predecessor_evidence":1,"no_auto_bind":17,"archived":1,"empty_stubs":2,"unresolved_hc_template_claimants":3}
    assert {r["repository"] for r in rows if r["archived"]}=={"thebrazenbeard/conditioning"}
    assert {r["repository"] for r in rows if r["lineage_status"]=="EMPTY_STUB"}=={"thebrazenbeard/vera-apk","thebrazenbeard/vera-habitat"}
    assert {r["repository"] for r in rows if r["lineage_status"]=="UNRESOLVED_HC_TEMPLATE_CANONICALITY"}=={"thebrazenbeard/self","thebrazenbeard/hc-brain","thebrazenbeard/bt2"}
    assert all(len(r["observed_head"])==40 for r in rows)
    assert all(r["availability_implies_activation"] is False for r in rows)
    assert d["project_control"]["control_plane"]=="thebrazenbeard/vera-control-plane"
    assert d["supabase"]["vera"]["schema_owners"]["radar"]=="thebrazenbeard/chat-communication-bus"
    assert d["supabase"]["vera"]["schema_owners"]["redworm"].startswith("UNRESOLVED_")
    assert d["bus"]["current_vera_lane"]=="bus/vera-v2"
    assert d["bus"]["provider_historical_lane_is_current_route_authority"] is False
    assert d["cleanup"]["delete_repositories"]==[]
    assert d["hostile_qualification"]["status"]=="PARTIAL_PASS_WITH_BLOCKERS"
    return {"status":"PASS","repositories":59,"blockers":len(d["hostile_qualification"]["blockers"]),"gaps":len(d["hostile_qualification"]["gaps"])}
if __name__=="__main__": print(json.dumps(validate(),indent=2,sort_keys=True))
