# Arquivo __init__.py para o pacote app.pages
# Este arquivo permite que o Python reconheça este diretório como um pacote importável

# Exportar módulos explicitamente
from . import main_app
from . import about
from . import haversine_page
from . import report_page
from .algorithms import astar_page, bfs_page, fuzzy_page