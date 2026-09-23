from tools.validate_live_portfolio_v2 import validate
def test_live_portfolio_map_v2():
    r=validate()
    assert r["status"]=="PASS"
    assert r["repositories"]==59
