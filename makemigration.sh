#!/bin/bash
set -e

read -p "Enter the migration message (no quotes required): " message

alembic revision --autogenerate -m "$message"