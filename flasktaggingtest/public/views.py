# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""

import re

from flask import (
    Blueprint, request, render_template, flash, url_for,
    redirect, session)

from flasktaggingtest.utils import flash_errors
from flasktaggingtest.public.forms import TaggingForm, TagDBForm

blueprint = Blueprint('public', __name__, static_folder="../static")


def get_tags_choices():
    """
    Loads all saved tags, and all tags currently mapped,
    from session store.
    """

    # Would be something like this if fetching tags from the DB:
    # tags_choices_all = [(str(o.id), o.title) for o in Tag.query
    #     .all()]
    # For session-storage example, is like this:
    tags_choices_all = [
        (str(id), title)
        for id, title in enumerate(session.get('tags', [])) if id]

    # Would be something like this if fetching tags from the DB:
    # tags_choices = [(str(o.id), o.title) for o in Tag.query
    #         .join(Tag.posts)
    #         .filter_by(id=post.id)
    #         .all()]
    # For session-storage example, is like this:
    tags_choices = [
        (id, title)
        for id, title in tags_choices_all
        if int(id) in session.get('tag_map', [])]

    return (tags_choices_all, tags_choices)


@blueprint.route("/")
def home():
    form = TaggingForm(request.form)
    tags_choices_all, tags_choices = get_tags_choices()
    print '-------------------home----------------'
    print 'form.tags_field.data: ', form.tags_field.data
    print "tags_choices_all: ", tags_choices_all
    print 'tags_choices: ', tags_choices
    form.tags_field.choices = tags_choices_all
    form.tags_field.default = [id for id, title in tags_choices]

    # Make the new default values take effect - see:
    # http://stackoverflow.com/a/5519971/2066849
    form.tags_field.process(request.form)

    print '-------------------end----------------'
    return render_template("public/home.html", form=form)


@blueprint.route("/home1")
def home1():
    form = TagDBForm(request.form)

    # Make the new default values take effect - see:
    # http://stackoverflow.com/a/5519971/2066849
    form.tags_field.process(request.form)

    print '-------------------end----------------'
    return render_template("public/home1.html", form=form)


@blueprint.route("/save-tags/", methods=["POST"])
def save_tags():
    print '-------------------save tags----------------'
    form = TaggingForm(request.form)
    print 'form.tags_field.data: ', form.tags_field.data
    tags_choices_all, tags_choices = get_tags_choices()
    tags_choices_dict = dict(tags_choices)
    tags_choices_new = []
    print 'tags_choices: ', tags_choices
    print 'tags_choices_dict: ', tags_choices_dict
    print 'tags_choices_new: ', tags_choices_new

    # Dynamically add non-recognized choices (with ID and title
    # set to the title), for select choice validation purposes.
    for v in request.form.getlist('tags_field'):
        if (
                v and
                re.match(r'^[A-Za-z0-9_\- ]+$', v) and
                not(v in tags_choices_dict)):
            tags_choices_new.append((v, v))

    form.tags_field.choices = tags_choices_all + tags_choices_new

    form.tags_field.default = [id for id, title in tags_choices]

    # Make the new default values take effect - see:
    # http://stackoverflow.com/a/5519971/2066849
    form.tags_field.process(request.form)

    # Note: DB storage examples (in comments) are based on an
    # implementation of this in SQLAlchemy (declarative / ORM version).
    if form.validate_on_submit():
        if form.tags_field.data:
            tags_ids = []

            # Find all integer IDs of submitted tags.
            for v in form.tags_field.data:
                try:
                    tag_id = int(v)
                    tags_ids.append(tag_id)
                except ValueError:
                    pass

            # Save all tag mappings for recognized integer IDs now.
            # Would be something like this if fetching tags from the DB:
            # post.tags = Tag.query
            #     .filter(Tag.id.in_(tags_ids)).all()
            # ids_found = [str(o.id) for o in post.tags]
            # For session-storage example, is like this:
            session['tag_map'] = [
                int(id) for id, title in tags_choices_all if (id in tags_ids)]
            ids_found = [str(id) for id in session['tag_map']]
            print form.tags_field.data
            for v in form.tags_field.data:
                # Cases where a submitted tag ID is either
                # a non-integer, or where tag lookup by ID failed.
                if not (v in ids_found):
                    # Try and do tag lookup by title.
                    try:
                        # Would be something like this if fetching tags
                        # from the DB:
                        # existing_tag = Tag.query
                        #     .filter_by(title=v).first()
                        # For session-storage example, is like this:
                        existing_tag = [
                            int(id)
                            for id, title in tags_choices_all
                            if (title == v)][0]
                    except IndexError:
                        existing_tag = None

                    if existing_tag:
                        # If tag lookup by title succeeded, then
                        # add the tag ID to the mapping.
                        # Would be something like this if fetching tags
                        # from the DB:
                        # post.tags.append(existing_tag)
                        # For session-storage example, is like this:
                        session['tag_map'].append(existing_tag)
                    elif re.match(r'^[A-Za-z0-9_\- ]+$', v):
                        # For session-storage example, avoid having a
                        # tag with ID 0, by making the first element
                        # of the list an empty string.
                        if not session.get('tags'):
                            session['tags'] = ['']

                        # Otherwise, create a new tag, and map it.
                        # Would be something like this if fetching tags
                        # from the DB:
                        # new_tag = Tag(title=v)
                        # db.session.add(new_tag)
                        # post.tags.append(new_tag)
                        # For session-storage example, is like this:
                        session['tags'].append(v)
                        new_tag = len(session['tags']) - 1
                        session['tag_map'].append(new_tag)
        else:
            # Would be something like this if fetching tags from the DB:
            # post.tags = []
            # For session-storage example, is like this:
            session['tag_map'] = []

        flash("Tags saved. %s" % session['tag_map'], 'success')
    else:
        flash_errors(form)

    print '-------------------end tags----------------'
    return redirect(url_for("public.home"))


@blueprint.route("/save-tags1/", methods=["POST"])
def save_tags1():
    print '-------------------save tags----------------'
    form = TaggingForm(request.form)
    print 'form.tags_field.data: ', form.tags_field.data
    tags_choices = form.tags_field.choices
    print 'tags_choices: ', tags_choices
    print '-------------------end tags----------------'
    return redirect(url_for("public.home"))
