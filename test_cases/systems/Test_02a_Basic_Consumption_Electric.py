################################################
# Test 2a - Basic_Consumption_Electric         #
################################################

# import all necessary model information
import os
import timeit
import json
from dbimat.source.model_base.ModelBase import *


class Model_Test_2a(ModelBase):

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
            ports[name] = {'electric':0, 'H2':0} - transcript the components ports to the model
        """

        name = 'RE'
        self.components[name] = Source(stream_type=StreamEnergy.ELECTRIC, size=1000,
                                       technology=Source.Technology.PV_ROOF, active=True)

        name = 'Storage_El'
        self.components[name] = Storage_Electrical(size=500, initial_value=500)

        name = 'Consumer_El'
        self.components[name] = Consumer(stream_type=StreamEnergy.ELECTRIC, size=1100)

        self.add_branch(branch_name='El_1',
                        branch_type=StreamEnergy.ELECTRIC,
                        port_connections=[
                            ('RE', StreamDirection.stream_out_of_component),
                            ('Consumer_El', StreamDirection.stream_into_component),
                            ('Storage_El', StreamDirection.stream_bidirectional)])

        # define operation rules
        self.passive_priorityRules.extend(['Consumer_El'])

        self.set_time_resolution(60)
        self.profile_len = 20

        # --- do automated declaration processing ---
        self.init_structure()  # init names, ports, branches

    def report(self):
        for name in list(self.components.keys()):
            logging.info('ports of ' + name + ': {}'.format(self.ports[name]))


def run(logging_level: LoggingLevels):
    # define model (with integrated check routines)
    model1 = Model_Test_2a(database_name='xxx', db_location='server', logging_level=logging_level)

    # run system (multiple model solve steps)
    model1.run()
    model1.calculate_costs()

def run_local(logging_level: LoggingLevels):
    my_system_model = Model_Test_2a(database_name='dbi_mat', db_location='local', logging_level=logging_level)
    my_system_model.run()
    my_system_model.calculate_costs()

if __name__ == '__main__':
    #run(LoggingLevels.DEBUG)
    run_local(LoggingLevels.DEBUG)
