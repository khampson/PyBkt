# Load the files in gvim in remote tabs, first starting a server in which to load them.
gvim --servername GV_PYBKT
gvim --servername GV_PYBKT --remote-tab fbsorter.py \
					fbutils.py \
					fset.py \
					pybkt.py \
					gvo_bkt.sh


