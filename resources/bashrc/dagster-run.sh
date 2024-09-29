dagster-run() {
  _dir="${DAGSTER_CODE_LOCATIONS}/${1}";
  if [[ ! -d "${_dir}" ]]; then
    echo "Code location does not exist.";
  else
    # shellcheck disable=SC2164
    pushd "${_dir}";
    dagster dev;
  fi;
  # shellcheck disable=SC2164
  popd;
}
