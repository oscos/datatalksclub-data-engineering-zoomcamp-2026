# ----------------------------------------
# JupyterLab + Data Engineering Environment
# ----------------------------------------
FROM jupyter/datascience-notebook:python-3.11

# Switch to root for system-level installs
USER root

# Install additional Python packages
RUN pip install --no-cache-dir \
    sqlalchemy \
    psycopg2-binary \
    seaborn \
    scikit-learn

# Create work directory and fix permissions
RUN mkdir -p /home/jovyan/work && \
    fix-permissions /home/jovyan/work

# Set working directory
WORKDIR /home/jovyan/work

# Ensure JupyterLab is enabled
ENV JUPYTER_ENABLE_LAB=yes

# Switch back to the notebook user
USER $NB_UID

EXPOSE 8888

