# import all necessary model information
from dbimat.source.model_base.ModelBase import *

class Model_Test4(ModelBase):

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
        # self.components[name] = Source(size=1000, category='pv', KPI=baseLib['KPI']['EnergySupply']['Wind'], profile=my_profile, active=True)
        self.components[name] = Source(stream_type=StreamEnergy.ELECTRIC, technology=Source.Technology.WIND_ONSHORE, size=15,
                                       active=True)

        name = 'Consumer_El'
        self.components[name] = Consumer(stream_type=StreamEnergy.ELECTRIC, active=True, size=10)

        name = 'Storage_El'
        self.components[name] = Storage_Electrical(size=10, initial_value=10)

        name = 'Ely'
        self.components[name] = Electrolyser(size=10)

        # Energy Dump:
        # name = 'dump_el'
        # self.components[name] = Source(controlled_medium='electric', technology='Grid')
        # self.connections[name] = [(('Ely', 'electric'), (name, 'electric'))]

        name = 'Storage_Gas'
        self.components[name] = Storage_Gas(size=10, stream_type=StreamMass.HYDROGEN, pressure_max=30e5,
                                            pressure_min=5e5, storage_volume=10000,
                                            initial_value=0)

        name = 'Generator_H2'
        self.components[name] = CHP_Plant(technology=CHP_Plant.Technology.H2, size=10)

        # H2 Dump:
        # name = 'dump_h2'
        # self.components[name] = Source(controlled_medium='H2', technology='Grid')
        # self.connections[name] = [(('Ely', 'H2'), (name, 'H2'))]

        name = 'Netz'
        self.components[name] = Grid(stream_type=StreamEnergy.ELECTRIC)

        self.set_time_resolution(60)
        # define operation rules

        self.add_branch(branch_name='El', branch_type=StreamEnergy.ELECTRIC,
                        port_connections=[
                            ('EE', StreamDirection.stream_out_of_component),
                            ('Generator_H2', StreamDirection.stream_out_of_component),
                            ('Storage_El', StreamDirection.stream_bidirectional),
                            ('Consumer_El', StreamDirection.stream_into_component),
                            ('Netz', StreamDirection.stream_bidirectional)])

        self.add_branch(branch_name='H2', branch_type=StreamMass.HYDROGEN,
                        port_connections=[
                            ('Ely', StreamDirection.stream_out_of_component),
                            ('Generator_H2', StreamDirection.stream_into_component),
                            ('Storage_Gas', StreamDirection.stream_out_of_component),
                            ('Storage_Gas', StreamDirection.stream_into_component)
                        ])

        self.passive_priorityRules.extend(['Consumer_El', 'Storage_El', 'Ely'])

        self.loop_control_rules.update({'electric': ['Netz'],
                                        'H2': ['Ely']
                                        })

        # --- do automated declaration processing ---
        self.init_structure()  # init names, ports, branches

    def report(self):
        for name in list(self.components.keys()):
            logging.info('ports of ' + name + ': {}'.format(self.ports[name]))


def run_local(logging_level: LoggingLevels):
    my_system_model = Model_Test4(database_name='dbi_mat', db_location='local', logging_level=logging_level)
    my_system_model.run()
    my_system_model.calculate_costs()

if __name__ == '__main__':
    run_local(logging_level=LoggingLevels.CRITICAL)
