import pytest
from brownie import interface, chain, Wei, ZERO_ADDRESS

@pytest.fixture(scope="function", autouse=True)
def shared_setup(fn_isolation):
    pass


@pytest.fixture(scope='module')
def stranger(accounts):
    return accounts[9]


@pytest.fixture
def lido():
    return interface.Lido('0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84')


@pytest.fixture
def dao_acl():
    return interface.ACL('0x9895F0F17cc1d1891b6f18ee0b483B6f221b37Bb')


@pytest.fixture(scope='module')
def dao_voting(interface):
    return interface.Voting('0x2e59A20f205bB85a89C53f1936454680651E618e')


@pytest.fixture
def dao_oracle():
    return interface.LidoOracle('0x442af784A788A5bd6F42A01Ebe9F287a871243fb')


@pytest.fixture
def acc_oracles(accounts):
    return [
        accounts.at('0x140Bd8FbDc884f48dA7cb1c09bE8A2fAdfea776E', force=True),
        accounts.at('0x1d0813bf088BE3047d827D98524fBf779Bc25F00', force=True),
        accounts.at('0x404335BcE530400a5814375E7Ec1FB55fAff3eA2', force=True),
        accounts.at('0x946D3b081ed19173dC83Cd974fC69e1e760B7d78', force=True),
        accounts.at('0x007DE4a5F7bc37E2F26c0cb2E8A95006EE9B89b5', force=True)
    ]


class Helpers:
    accounts = None
    eth_banker = None
    dao_voting = None

    @staticmethod
    def fund_with_eth(addr, amount = '1000 ether'):
        Helpers.eth_banker.transfer(to=addr, amount=amount)

    @staticmethod
    def filter_events_from(addr, events):
      return list(filter(lambda evt: evt.address == addr, events))

    @staticmethod
    def assert_single_event_named(evt_name, tx, evt_keys_dict = None):
      receiver_events = Helpers.filter_events_from(tx.receiver, tx.events[evt_name])
      assert len(receiver_events) == 1
      if evt_keys_dict is not None:
        assert dict(receiver_events[0]) == evt_keys_dict
      return receiver_events[0]

    @staticmethod
    def pass_and_exec_dao_vote(vote_id):
        print(f'executing vote {vote_id}')

        # together these accounts hold 15% of LDO total supply
        ldo_holders = [
            '0x3e40d73eb977dc6a537af587d48316fee66e9c8c',
            '0xb8d83908aab38a159f3da47a59d84db8e1838712',
            '0xa2dfc431297aee387c05beef507e5335e684fbcd'
        ]

        helper_acct = Helpers.accounts[0]

        for holder_addr in ldo_holders:
            print(f'voting from {holder_addr}')
            helper_acct.transfer(holder_addr, '0.1 ether')
            account = Helpers.accounts.at(holder_addr, force=True)
            Helpers.dao_voting.vote(vote_id, True, False, {'from': account})

        # wait for the vote to end
        chain.sleep(3 * 60 * 60 * 24)
        chain.mine()

        assert Helpers.dao_voting.canExecute(vote_id)
        Helpers.dao_voting.executeVote(vote_id, {'from': helper_acct})

        print(f'vote {vote_id} executed')



@pytest.fixture(scope='module')
def helpers(accounts, dao_voting):
    Helpers.accounts = accounts
    Helpers.eth_banker = accounts.at('0xBE0eB53F46cd790Cd13851d5EFf43D12404d33E8', force=True)
    Helpers.dao_voting = dao_voting
    return Helpers
