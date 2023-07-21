from dbimat.source.model_base.ModelBase import *

class Model_Test_05_Mischner(ModelBase):

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

        name = 'Source_H2'
        self.components[name] = Source(active=True,
                                       stream_type=StreamMass.HYDROGEN,
                                       generic_technical_input=GenericTechnicalInput(
                                           pressures=[
                                               Pressure(
                                                   stream_type_of_port=StreamMass.HYDROGEN,
                                                   stream_direction_of_port=StreamDirection.stream_out_of_component,
                                                   pressure_value=61.6 * 100000,
                                                   unit=Unit.Pa
                                               )
                                           ],
                                           temperatures=[
                                               Temperature(
                                                   stream_type_of_port=StreamMass.HYDROGEN,
                                                   stream_direction_of_port=StreamDirection.stream_out_of_component,
                                                   temperature_value=273.15 + 10,
                                                   unit=Unit.K
                                               )
                                           ]
                                       )
                                       )

        name = 'Consumer_H2'
        self.components[name] = Consumer(stream_type=StreamMass.HYDROGEN, active=True)

        compression_efficiencies = {}
        compression_efficiencies['isentropic'] = 0.72
        compression_efficiencies['electrical'] = 1
        compression_efficiencies['mechanical'] = 1

        name = 'Compressor_H2'
        self.components[name] = Compressor(size=50000, stream_type=StreamMass.HYDROGEN, stages=1,
                                           pressure_out=80 * 100000, compression_efficiencies=compression_efficiencies)

        name = 'Pipeline_H2'
        self.components[name] = Pipeline_Segment(technology=Pipeline_Segment.Technology.ONSHORE_UNDERGROUND,
                                                 stream_type=StreamMass.HYDROGEN,
                                                 inner_diameter_in_m=1,
                                                 length=250000, roughness_in_mm=0.005e-3, inlet_altitude=140,
                                                 outlet_altitude=0)

        name = 'Netz'
        self.components[name] = Grid(stream_type=StreamEnergy.ELECTRIC)

        branch_name = 'H2_2'
        self.add_branch(branch_name=branch_name, branch_type=StreamMass.HYDROGEN, port_connections=[
            ('Source_H2', StreamDirection.stream_out_of_component),
            ('Compressor_H2', StreamDirection.stream_into_component),
        ])

        branch_name = 'H2_3'
        self.add_branch(branch_name=branch_name, branch_type=StreamMass.HYDROGEN, port_connections=[
            ('Pipeline_H2', StreamDirection.stream_into_component),
            ('Compressor_H2', StreamDirection.stream_out_of_component)])

        branch_name = 'H2_Consumer'
        self.add_branch(branch_name=branch_name, branch_type=StreamMass.HYDROGEN, port_connections=[
            ('Pipeline_H2', StreamDirection.stream_out_of_component),
            ('Consumer_H2', StreamDirection.stream_into_component)
        ])

        branch_name = 'Electric'
        self.add_branch(branch_name=branch_name, branch_type=StreamEnergy.ELECTRIC,
                        port_connections=[
                            ('Compressor_H2', StreamDirection.stream_into_component),
                            ('Netz', StreamDirection.stream_bidirectional)])

        # --- Set time resolution of model ---
        self.set_time_resolution(60)

        # define operation rules
        self.passive_priorityRules.extend(['Pipeline_H2'])

        self.loop_control_rules.update({'Electric': ['Netz'],
                                        'H2_3': ['Pipeline_H2']
                                        })

        # --- Add profiles -------

        self.add_profile_to_component_port(component_name='Source_H2',
                                           port_stream_type=StreamMass.HYDROGEN,
                                           port_stream_direction=StreamDirection.stream_out_of_component,
                                           profile=[3139382 * 0.0899],
                                           profile_type=PhysicalQuantity.stream,
                                           time_resolution=60)
        self.add_profile_to_component_port(component_name='Consumer_H2',
                                           port_stream_type=StreamMass.HYDROGEN,
                                           port_stream_direction=StreamDirection.stream_into_component,
                                           profile=[-3139382 * 0.0899],
                                           profile_type=PhysicalQuantity.stream)

        # --- do automated declaration processing ---
        self.init_structure()  # init names, ports, branches

    def report(self):
        for name in list(self.components.keys()):
            logging.info('ports of ' + name + ': {}'.format(self.ports[name]))


def run_local(logging_level: LoggingLevels):
    model1 = Model_Test_05_Mischner(database_name='dbi_mat', db_location='local', logging_level=logging_level)

    # define model (with integrated check routines)
    model1.run()
    model1.calculate_costs()

    pressure_out_mischner = 61.60 * 100000
    compression_power_mischner = 35997
    pressure_out_port = model1.components['Pipeline_H2'].get_ports_by_type_and_sign(StreamMass.HYDROGEN,
                                                                                    StreamDirection.stream_out_of_component)
    electrical_port = model1.components['Compressor_H2'].get_ports_by_type_and_sign(StreamEnergy.ELECTRIC,
                                                                                    StreamDirection.stream_into_component)
    error_pressure = (abs(pressure_out_port.get_pressure()) - pressure_out_mischner) / pressure_out_mischner * 100
    error_power = (abs(electrical_port.get_stream()) - compression_power_mischner) / compression_power_mischner * 100

    maximum_error = 2
    if (abs(error_power) > maximum_error or abs(error_pressure) > maximum_error):
        print('relative error p_out {} %.'.format(error_pressure))
        print('relative error power_out {} %.'.format(error_power))
        print('max relative error larger than {} %.'.format(maximum_error))
        raise AssertionError('max relative error larger than {} %.'.format(maximum_error))


if __name__ == '__main__':
    run_local(LoggingLevels.WARNING)

