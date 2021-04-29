import pytest
import brownie
from brownie import Wei, chain, reverts


UPGRADE_VOTE_ID = 63
DENOMINATION_OFFSET = 1000_000_000


@pytest.fixture(scope='module')
def pass_vote(helpers):
    helpers.pass_and_exec_dao_vote(UPGRADE_VOTE_ID)


@pytest.fixture
def oracle(dao_oracle, pass_vote):
    return dao_oracle


def test_acls(oracle, dao_acl, dao_voting):
    voting_addr = dao_voting.address
    assert dao_acl.hasPermission(voting_addr, oracle, oracle.MANAGE_MEMBERS())
    assert dao_acl.hasPermission(voting_addr, oracle, oracle.MANAGE_QUORUM())
    assert dao_acl.hasPermission(voting_addr, oracle, oracle.SET_BEACON_SPEC())
    assert dao_acl.hasPermission(voting_addr, oracle, oracle.SET_REPORT_BOUNDARIES())
    assert dao_acl.hasPermission(voting_addr, oracle, oracle.SET_BEACON_REPORT_RECEIVER())


def test_config(lido, oracle, dao_voting, accounts):
    assert oracle.getVersion() == 1

    with brownie.reverts('ALREADY_INITIALIZED'):
        voting_acct = accounts.at(dao_voting.address, force=True)
        oracle.initialize_v2(1000, 500, {'from': voting_acct, 'gas_price': 0})

    assert oracle.getVersion() == 1
    assert oracle.getLido() == lido.address
    assert oracle.getBeaconReportReceiver() == "0x0000000000000000000000000000000000000000"
    assert oracle.getAllowedBeaconBalanceAnnualRelativeIncrease() == 1000  # 10% yearly increase
    assert oracle.getAllowedBeaconBalanceRelativeDecrease() == 500  # 5% moment decrease
    assert oracle.getCurrentOraclesReportStatus() == 0
    assert oracle.getCurrentReportVariantsSize() == 0
    assert oracle.getBeaconSpec() == (225, 32, 12, 1606824023)
    assert oracle.getLastCompletedReportDelta() == (0, 0, 0) # no data until first push


def sleep(epoch_delta):
    chain.mine(timedelta = 32 * 12 * epoch_delta)
    return epoch_delta


def test_report_beacon(lido, oracle, acc_oracles):
    sleep(225)
    epoch = (oracle.getCurrentEpochId() // 225) * 225

    (_, beacon_validators, beacon_balance) = lido.getBeaconStat()
    total_pooled_ether = lido.totalSupply()

    balance_delta = Wei('1 ether')
    balance_report = (beacon_balance + balance_delta) // DENOMINATION_OFFSET

    tx = oracle.reportBeacon(epoch, balance_report, beacon_validators, {'from': acc_oracles[0], 'gas_price': 0})
    tx = oracle.reportBeacon(epoch, balance_report, beacon_validators, {'from': acc_oracles[1], 'gas_price': 0})
    tx = oracle.reportBeacon(epoch, balance_report, beacon_validators, {'from': acc_oracles[2], 'gas_price': 0})

    assert tx.events['Completed']['epochId'] == epoch
    assert tx.events['Completed']['beaconBalance'] == balance_report * DENOMINATION_OFFSET
    assert tx.events['Completed']['beaconValidators'] == beacon_validators

    (_, new_beacon_validators, new_beacon_balance) = lido.getBeaconStat()
    assert new_beacon_balance == beacon_balance + balance_delta
    assert new_beacon_validators == beacon_validators

    assert oracle.getCurrentOraclesReportStatus() == 0
    assert oracle.getCurrentReportVariantsSize() == 0

    (post_total_ether, pre_total_ether, _) = oracle.getLastCompletedReportDelta()
    assert post_total_ether == total_pooled_ether + balance_delta
    assert pre_total_ether == total_pooled_ether
