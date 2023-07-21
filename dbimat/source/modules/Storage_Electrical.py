from dbimat.source.modules.Storage import Storage
from dbimat.source.basic.Streamtypes import StreamMass, StreamEnergy
from dbimat.source.basic.Quantities import PhysicalQuantity
from dbimat.source.helper._FunctionDef import range_limit
from dbimat.source.helper._FunctionDef import in_range
from dbimat.source.basic.Streamtypes import StreamDirection
from dbimat.source.model_base.Dataclasses.TechnicalDataclasses import GenericTechnicalInput
import math
import logging
from enum import Enum, auto


class Storage_Electrical(Storage):
    class Technology(Enum):
        BATTERY = auto()

    def __init__(self, size=None, charge_power=math.inf, technology=None, active=False, initial_value=None,
                 efficiency: float = 1.0, new_investment=False, economical_parameters=None,
                 generic_technical_input: GenericTechnicalInput = None):
        super().__init__(size, charge_power, technology, active, initial_value, efficiency,
                         new_investment, economical_parameters=economical_parameters,
                         generic_technical_input=generic_technical_input)

        self.load_management_profile = None
        self.calculated_charge_intervall = None
        self.theoretical_charge = None
        self.highload_buffer = 0
        self._add_port(port_type=StreamEnergy.ELECTRIC,
                       component_ID=self.component_id,
                       fixed_status=active, sign=StreamDirection.stream_bidirectional)

        if technology is not None:
            self.technology = technology
        else:
            self.technology = Storage_Electrical.Technology.BATTERY

    def run(self, port_id, branch_information, runcount=0):
        """run object code, a discharge rate needs to be specified by data"""

        self.status = 0  # set default status with 0:ok; >0:warning; <0:error

        # reset buffer if runcount is zero
        if runcount == 0:
            self.buffer_old = 0 if self.buffer_init is None else self.buffer_init
            self.buffer_new = 0 if self.buffer_init is None else self.buffer_init
            self.runcount_old = 0

        # only apply taken action to storage if run count change
        if runcount != self.runcount_old:
            self.runcount_old = runcount
            self.buffer_old = self.buffer_new
        # myInputs_shaving = self._run_peak_shaving(myInputs[self.controlled_medium])

        # calculate energy flow
        [controlled_port, power_stream, loop_control] = self._calc_control_var(port_id, branch_information[
            PhysicalQuantity.stream])
        # set flow by profile no matter if active or not
        if self.active & (not loop_control):
            if self.charge_power > self.energy_to_power(self.size):
                power_stream = self.energy_to_power(self.size)
            else:
                power_stream = self.charge_power

        power_stream = range_limit(power_stream, -self.charge_power, self.charge_power)

        energy_flow = self.power_to_energy(power_stream)
        # add the flows to the storage
        if energy_flow < 0:
            self.buffer_new = self.buffer_old - energy_flow * self.efficiency
        else:
            self.buffer_new = self.buffer_old - energy_flow / self.efficiency

        # limit flows to the system
        if self.size is not None:
            if self.buffer_new > self.size:
                diff = self.energy_to_power(self.buffer_new - self.size) / self.efficiency
                power_stream += diff
                self.buffer_new = self.size
            elif self.buffer_new < 0:
                diff = self.energy_to_power(self.buffer_new) * self.efficiency
                power_stream += diff
                self.buffer_new = 0

        if runcount >= len(self.component_technical_results.component_history['storage_level']):
            self.component_technical_results.component_history['storage_level'].append(0)
        self.component_technical_results.component_history['storage_level'][runcount] = self.buffer_new

        # return output -> discharge storage
        self.ports[controlled_port].set_stream(runcount, power_stream)

        if runcount > 0:
            if power_stream < 0:
                if abs(self.component_technical_results.component_history['storage_level'][runcount] - self.component_technical_results.component_history['storage_level'][
                    runcount - 1] + self.power_to_energy(
                    power_stream * self.efficiency)) > 1e-2:
                    logging.warning(
                        'The difference between buffer level change and charge/discharge energy is {} \n At Timestep {}'.format(
                            abs(self.component_technical_results.component_history['storage_level'][runcount] -
                                self.component_technical_results.component_history['storage_level'][
                                    runcount - 1] + self.power_to_energy(
                                power_stream * self.efficiency)),
                            runcount))
                    self.status = 1
            else:
                if abs(self.component_technical_results.component_history['storage_level'][runcount] - self.component_technical_results.component_history['storage_level'][
                    runcount - 1] + self.power_to_energy(
                    power_stream / self.efficiency)) > 1e-2:
                    logging.warning(
                        'The difference between buffer level change and charge/discharge energy is {} \n At Timestep {}'.format(
                            abs(self.component_technical_results.component_history['storage_level'][runcount] -
                                self.component_technical_results.component_history['storage_level'][
                                    runcount - 1] + self.power_to_energy(
                                power_stream / self.efficiency)),
                            runcount))
                    self.status = 1
