import json

import pytest

from app.storage import migrations
from app.storage.migrations import DataTooNewError, MigrationContext, MigrationError


def make_context(tmp_path):
    app_data = tmp_path / "appdata"
    data_dir = tmp_path / "data"
    app_data.mkdir()
    data_dir.mkdir()
    (app_data / "account.json").write_text('{"username": "a"}', encoding="utf-8")
    (app_data / "subheads.json").write_text('{"treesa": [], "daily": []}', encoding="utf-8")
    return MigrationContext(app_data=app_data, data_dir=data_dir)


def stored_version(context):
    return json.loads((context.app_data / migrations.STATE_FILE).read_text(encoding="utf-8"))["data_version"]


def test_files_without_a_state_file_are_the_baseline_and_get_one(tmp_path):
    context = make_context(tmp_path)
    assert migrations.run(context, target=1) == 1
    assert stored_version(context) == 1
    assert not (context.app_data / migrations.BACKUP_FOLDER).exists()  # nothing to migrate, nothing to back up


def test_runs_each_migration_in_order_after_a_backup(tmp_path):
    context = make_context(tmp_path)
    order = []

    def one_to_two(ctx):
        order.append(1)
        (ctx.app_data / "account.json").write_text('{"username": "a", "extra": 1}', encoding="utf-8")

    def two_to_three(ctx):
        order.append(2)

    assert migrations.run(context, target=3, migrations={1: one_to_two, 2: two_to_three}) == 3
    assert order == [1, 2]
    assert stored_version(context) == 3
    backups = list((context.app_data / migrations.BACKUP_FOLDER).iterdir())
    assert len(backups) == 1
    assert json.loads((backups[0] / "account.json").read_text(encoding="utf-8")) == {"username": "a"}  # the old copy


def test_a_failed_migration_keeps_the_old_version_and_the_backup(tmp_path):
    context = make_context(tmp_path)

    def one_to_two(ctx):
        raise RuntimeError("boom")

    with pytest.raises(MigrationError):
        migrations.run(context, target=2, migrations={1: one_to_two})
    assert migrations.read_state(context.app_data)["data_version"] == 1
    assert len(list((context.app_data / migrations.BACKUP_FOLDER).iterdir())) == 1


def test_a_missing_migration_is_an_error(tmp_path):
    context = make_context(tmp_path)
    with pytest.raises(MigrationError):
        migrations.run(context, target=2, migrations={})


def test_files_from_a_newer_version_are_refused(tmp_path):
    context = make_context(tmp_path)
    migrations.write_state(context.app_data, 5)
    with pytest.raises(DataTooNewError):
        migrations.run(context, target=2, migrations={})
    assert stored_version(context) == 5  # untouched


def test_an_unreadable_state_file_is_treated_as_the_baseline(tmp_path):
    context = make_context(tmp_path)
    (context.app_data / migrations.STATE_FILE).write_text("not json", encoding="utf-8")
    assert migrations.read_state(context.app_data)["data_version"] == 1


def test_only_the_newest_backups_are_kept(tmp_path):
    context = make_context(tmp_path)
    root = context.app_data / migrations.BACKUP_FOLDER
    for number in range(migrations.KEEP_BACKUPS + 3):
        (root / f"old-{number:02d}").mkdir(parents=True)
    migrations.backup(context.app_data, 1, 2)
    assert len(list(root.iterdir())) == migrations.KEEP_BACKUPS


def test_the_real_migration_table_covers_every_version():
    for version in range(1, migrations.DATA_VERSION):
        assert version in migrations.MIGRATIONS
