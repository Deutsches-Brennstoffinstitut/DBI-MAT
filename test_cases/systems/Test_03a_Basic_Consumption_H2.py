################################################
# Test 3 - Basic_Consumption_H2                #
################################################

from dbimat.source.model_base.ModelBase import *

class Model_Test_3(ModelBase):

    def __init__(self, database_name, db_location, logging_level: LoggingLevels = LoggingLevels.WARNING):
        # init
        super().__init__(database_name, db_location, logging_level)
        self.modeldir = inspect.getfile(self.__class__)

        self.basic_technical_settings = BasicTechnicalSettings(time_resolution=60,
                                                               absolute_model_error=1e-10)

        self.basic_economical_settings = BasicEconomicalSettings(reference_year=2021,
                                                                 start_year=2021,
                                                                 end_year=2030,
                                                                 basic_interest_rate=0.03,
                                                                 estimated_inflation_rate=0
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

        name = 'EE'
        self.components[name] = Source(stream_type=StreamEnergy.ELECTRIC, size=10, technology=Source.Technology.WIND_ONSHORE,
                                       active=True)

        # Energie Dump:
        name = "dump_el"
        self.components[name] = Grid(stream_type=StreamEnergy.ELECTRIC)

        name = 'ELY'
        self.components[name] = Electrolyser(size=15)

        name = 'Storage_Gas'
        self.components[name] = Storage_Gas(size=550000, stream_type=StreamMass.HYDROGEN, initial_value=0)

        # HYDROGEN Dump:
        name = "dump_HYDROGEN"
        self.components[name] = Grid(stream_type=StreamMass.HYDROGEN)

        name = 'Consumer_HYDROGEN'
        self.components[name] = Consumer(stream_type=StreamMass.HYDROGEN, active=False)

        self.add_branch(branch_name='El', branch_type=StreamEnergy.ELECTRIC,
                        port_connections=[
                            ('EE', StreamDirection.stream_out_of_component),
                            ('dump_el', StreamDirection.stream_bidirectional),
                            ('ELY', StreamDirection.stream_into_component)])

        self.add_branch(branch_name='H2', branch_type=StreamMass.HYDROGEN,
                        port_connections=[
                            ('ELY', StreamDirection.stream_out_of_component),
                            ('Storage_Gas', StreamDirection.stream_out_of_component),
                            ('Storage_Gas', StreamDirection.stream_into_component),
                            ('dump_HYDROGEN', StreamDirection.stream_bidirectional),
                            ('Consumer_HYDROGEN', StreamDirection.stream_into_component)])

        self.set_time_resolution(60)
        # define operation rules
        self.passive_priorityRules.extend(['ELY', 'dump_el'])
        # self.passive_priorityRules.extend(['Storage_Gas', 'dump_h2'])

        # --- do automated declaration processing ---
        self.init_structure()  # init names, ports, branches

    def report(self):
        for name in list(self.components.keys()):
            logging.info('ports of ' + name + ': {}'.format(self.ports[name]))


def run_local(logging_level: LoggingLevels):
    my_system_model = Model_Test_3(database_name='dbi_mat', db_location='local', logging_level=logging_level)
    my_system_model.run()
    my_system_model.calculate_costs()

if __name__ == '__main__':
    run_local(LoggingLevels.CRITICAL)
