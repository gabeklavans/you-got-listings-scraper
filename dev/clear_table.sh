#!/bin/bash
sqlite3 ./data/ygl.db "DELETE FROM $1"
