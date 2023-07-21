################################################
# Test 2b - Basic_Consumption_Electric         #
################################################

from dbimat.source.model_base.ModelBase import *

class Model_Test_2b(ModelBase):

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

        name = 'Netz'
        self.components[name] = Grid(stream_type=StreamEnergy.ELECTRIC)

        name = 'EE'
        self.components[name] = Source(technology=Source.Technology.WIND_ONSHORE, stream_type=StreamEnergy.ELECTRIC,
                                       size=20, active=True)

        name = 'Storage_El'
        self.components[name] = Storage_Electrical(size=100, initial_value=0)

        name = 'Consumer_El'
        self.components[name] = Consumer(stream_type=StreamEnergy.ELECTRIC, size=15)

        self.add_branch(branch_name='El_1', branch_type=StreamEnergy.ELECTRIC,
                        port_connections=[
                            ('Netz', StreamDirection.stream_bidirectional),
                            ('EE', StreamDirection.stream_out_of_component),
                            ('Storage_El', StreamDirection.stream_bidirectional),
                            ('Consumer_El', StreamDirection.stream_into_component)])
        self.set_time_resolution(60)
        # define operation rules
        self.passive_priorityRules.extend(['Consumer_El'])

        # --- do automated declaration processing ---
        self.init_structure()  # init names, ports, branches

    def report(self):
        for name in list(self.components.keys()):
            logging.info('ports of ' + name + ': {}'.format(self.ports[name]))

def run_local(logging_level: LoggingLevels):
    my_system_model = Model_Test_2b(database_name='dbi_mat', db_location='local', logging_level=logging_level)
    my_system_model.run()
    my_system_model.calculate_costs()

if __name__ == '__main__':
    run_local(LoggingLevels.CRITICAL)
