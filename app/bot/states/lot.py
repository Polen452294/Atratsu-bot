from aiogram.fsm.state import State, StatesGroup


class LotCreationStates(StatesGroup):
    route_from = State()
    route_to = State()
    distance_km = State()
    deadline_at = State()
    vehicle_type = State()
    weight_tons = State()
    volume_m3 = State()
    budget_rub = State()
    confirm = State()