

from pint import UnitRegistry
ureg = UnitRegistry()
Q_ = ureg.Quantity
ureg.define('molar = 1 * mole / liter = M')
ureg.define('times_recommended_concentration = 1 * microliter/microliter = x')
ureg.define('unit = 1 * gram/gram = U')
ureg.define('percent = 1 * microliter/microliter = %')