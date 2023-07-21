from dbimat.source.model_base.ModelBase import *

class Model_Test_07(ModelBase):

    def __init__(self, database_name, db_location, logging_level: LoggingLevels = LoggingLevels.WARNING):
        # init
        super().__init__(database_name, db_location, logging_level)
        self.modeldir = inspect.getfile(self.__class__)

        self.basic_technical_settings = BasicTechnicalSettings(time_resolution=60,
                                                               absolute_model_error=1e-10)

        self.basic_economical_settings = BasicEconomicalSettings(reference_year=2024,
                                                                 start_year=2024,
                                                                 end_year=2053,
                                                                 basic_interest_rate=0.07,
                                                                 estimated_inflation_rate=0.00
                                                                 )

        # --------------------------
        # --- declare components ---
        # --------------------------
        # insert your code here
        """ description of objects
            name = "any unique text string you like"
            components[name]  = model class     - create instance of class member
            connections[name] = [ a list of tuples of connection, where each tuple consists of a pair of tuples  ]
                                [ ((source definition), (target definition)) ]
                                [ ((name, 'electric'), ('mySource1', 'electric')), ((name, 'H2'), ('mySource2', 'special H2')) ]

            # automatic processing #
            names.append(name)                   - insert object into the list of known objects
            ports[name] = {'electric':0, 'H2':0} - transcript the copmonents ports to the model
        """

        name = 'Stromnetz'
        self.components[name] = Grid(stream_type=StreamEnergy.ELECTRIC,
                                     active=False,
                                     new_investment=True,
                                     economical_parameters=EconomicalParameters(
                                         stream_econ=[
                                             StreamEconParameters(
                                                 stream_type=StreamEnergy.ELECTRIC,
                                                 first_payment_year=2024,
                                                 amount_related_costs=Direction(
                                                     costs_out={'Strompreis': 0.20},
                                                     unit=Unit.euro_per_kWh
                                                 ),
                                                 price_dev=0.03
                                             )
                                         ]
                                     )
                                     )

        name = 'Brenner'
        self.components[name] = Consumer(stream_type=StreamEnergy.ELECTRIC,
                                         active=True,
                                         new_investment=True,
                                         economical_parameters=EconomicalParameters(
                                             component_capex=[
                                                 CAPEXParameters(
                                                     investment_cost=2000,
                                                     investment_year=2024,
                                                     name='Burner',
                                                     life_cycle=12,
                                                     risk_surcharge=0,
                                                     price_dev=0.03
                                                 )
                                             ],
                                             operational_opex=OPEXOperationalParameters(
                                                 opex_in_percentage_per_year=0.12)
                                         )
                                         )

        name = 'Wärmequelle'
        self.components[name] = Grid(stream_type=StreamEnergy.ELECTRIC,
                                     active=False,
                                     new_investment=True,
                                     economical_parameters=EconomicalParameters(
                                         stream_econ=[
                                             StreamEconParameters(
                                                 stream_type=StreamEnergy.ELECTRIC,
                                                 first_payment_year=2024,
                                                 amount_related_costs=Direction(
                                                     costs_out={'Strompreis': 0.06},
                                                     unit=Unit.euro_per_kWh
                                                 ),
                                                 price_dev=0.03
                                             )
                                         ]
                                     )
                                     )

        name = 'Wärmeverbraucher'
        self.components[name] = Consumer(stream_type=StreamEnergy.ELECTRIC,
                                         active=True,
                                         new_investment=False
                                         )

        branch_name = 'Electric'
        self.add_branch(branch_name=branch_name, branch_type=StreamEnergy.ELECTRIC,
                        port_connections=[
                            ('Brenner', StreamDirection.stream_into_component),
                            ('Stromnetz', StreamDirection.stream_bidirectional)])

        branch_name = 'Wärme'
        self.add_branch(branch_name=branch_name, branch_type=StreamEnergy.ELECTRIC,
                        port_connections=[
                            ('Wärmeverbraucher', StreamDirection.stream_into_component),
                            ('Wärmequelle', StreamDirection.stream_bidirectional)])

        # --- Add profiles -------
        self.add_stream_profile_to_port(component_name='Wärmeverbraucher',
                                        port_stream_type=StreamEnergy.ELECTRIC,
                                        port_stream_direction=StreamDirection.stream_into_component,
                                        profile=[-1401.2] * 10, unit=Unit.kW, time_resolution=60)
        self.add_stream_profile_to_port(component_name='Brenner',
                                        port_stream_type=StreamEnergy.ELECTRIC,
                                        port_stream_direction=StreamDirection.stream_into_component,
                                        profile=[-41.7] * 10, unit=Unit.kW, time_resolution=60)

        # --- do automated declaration processing ---
        self.init_structure()  # init names, ports, branches

    def report(self):
        for name in list(self.components.keys()):
            logging.info('ports of ' + name + ': {}'.format(self.ports[name]))

def reset():
    """
    Resetting the branch and component IDs is necessary since the IDs are a class variable, which leads to the problem
    that if you initialize more IDs by initializing multiple systems, the ID is continued
    :return:
    :rtype:
    """
    from dbimat.source.modules import GenericUnit
    from dbimat.source.model_base import Branches
    Branches.Branch.BRANCH_ID_COUNT = 0
    GenericUnit.GenericUnit.COMPONENT_ID_COUNT = 0

def run_local(logging_level: LoggingLevels):
    reset()
    my_system_model = Model_Test_07(database_name='dbi_mat', db_location='local', logging_level=logging_level)
    my_system_model.run()
    my_system_model.calculate_costs()
    maximum_error = 2
    annuities = my_system_model.system_results.get_annuity_of_all_components()
    annuities_expected = {'C01': 114.44653313035734,  # Stromnetz
                          'C02': 635.617972827661,  # Brenner
                          'C03': 1153.6869224622783,  # Wärmequelle
                          'C04': 0}  #Wärmeverbraucher
    for annuity_key, annuity in annuities.items():
        single_error = (abs(annuities_expected[annuity_key] - annuity) / annuities_expected[annuity_key]) * 100 if \
            annuities_expected[annuity_key] != 0 else 0

        if abs(single_error) > maximum_error:
            print(f'Relativer Fehler gleich {single_error} % im Vergleich zu erwarteten Werten.')
            raise AssertionError('Relativer Fehler größer als {} %.'.format(maximum_error))
    my_model_results = my_system_model.system_results
    #my_model_results.export_to_xlsx(filename='cost_calc', path='')

if __name__ == '__main__':
    run_local(logging_level=LoggingLevels.WARNING)


