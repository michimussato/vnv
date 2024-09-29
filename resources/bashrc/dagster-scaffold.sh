dagster-scaffold() {
  mkdir -p "${DAGSTER_CODE_LOCATIONS}"
  # shellcheck disable=SC2164
  pushd "${DAGSTER_CODE_LOCATIONS}";
  dagster project scaffold --name "${1}";
  # shellcheck disable=SC2164
  popd;
}
