$(function () {
    console.log("$('.session-scheduler').length");
    console.log($('.session-scheduler').length);
        try {
            $('.session-scheduler').each(
                function () {
                    var $this = $(this)
                    var settings = $(this).closest('.event-plugin-session-scheduler').find('.scheduler_settings_options').val();
                    var options = JSON.parse(settings)
                    console.log("options.session_scheduler_day_starts_at");
                    console.log(options.session_scheduler_day_starts_at);
                    var box_id = $(this).closest('.event-plugin-session-scheduler').find('.box_id').val();
                    var page_id = $(this).closest('.event-plugin-session-scheduler').find('.page_id').val();
                    //Override kendo function for deciding events with
                    kendo.ui.DayView.fn._arrangeColumns = function (element, top, height, slotRange) {
                        var startSlot = slotRange.start;
                        element = {element: element, slotIndex: startSlot.index, start: top, end: top + height};

                        var columns,
                            slotWidth = startSlot.clientWidth,
                            eventRightOffset = slotWidth * 0.10,
                            columnEvents,
                            eventElements = slotRange.events(),
                            slotEvents = kendo.ui.SchedulerView.collidingEvents(eventElements, element.start, element.end);

                        slotRange.addEvent(element);

                        slotEvents.push(element);

                        columns = kendo.ui.SchedulerView.createColumns(slotEvents);
                        //This is where the magic happens
                        var columnWidth = slotWidth / columns.length;
                        //var columnWidth = 100;
                        //Original code: var columnWidth = (slotWidth - eventRightOffset) / columns.length;
                        //This is where the magic ends
                        for (var idx = 0, length = columns.length; idx < length; idx++) {
                            columnEvents = columns[idx].events;
                            for (var j = 0, eventLength = columnEvents.length; j < eventLength; j++) {
                                columnEvents[j].element[0].style.width = columnWidth + 'px';
                                columnEvents[j].element[0].style.left = (this._isRtl ? this._scrollbarOffset(eventRightOffset) : 0) + startSlot.offsetLeft + idx * columnWidth + 2 + "px";
                            }

                        }
                    };

                    scheduler = $(this).kendoScheduler({
                        eventTemplate: $("#event-template").html(),
                        allDayEventTemplate: $("#event-template").html(),
                        date: new Date(options.session_scheduler_default_browse_date),
                        startTime: new Date(options.session_scheduler_default_browse_date + ' ' + options.session_scheduler_day_starts_at),
                        endTime: new Date(options.session_scheduler_default_browse_date + ' ' + options.session_scheduler_day_ends_at),
                        height: 800,
                        //width:options.session_scheduler_width,
                        views: options.session_scheduler_browsing_modes,
                        timezone: options.session_scheduler_timezone,
                        editable: false,
                        messages: options.session_scheduler_session_languages,
                        dataSource: {
                            batch: true,
                            transport: {
                                read: {
                                    url: base_url + '/get-scheduler-events/?tab=all-session&box_id=' + box_id + '&page_id=' + page_id,
                                    dataType: "json"

                                },

                            }
                            ,
                            serverSorting: true,
                            sort: {field: "title", dir: "desc"},
                            schema: {
                                model: {
                                    id: "id",
                                    fields: {
                                        id: {
                                            from: "id", type: "number"
                                        }
                                        ,
                                        title: {
                                            from: "Title", defaultValue: "No title", validation: {
                                                required: true
                                            }
                                        }
                                        ,
                                        start: {
                                            type: "date", from: "Start"
                                        }
                                        ,
                                        end: {
                                            type: "date", from: "End"
                                        }
                                        ,
                                        rsvp_date: {
                                            type: "date", from: "rsvp_date"
                                        }
                                        ,
                                        description: {
                                            from: "Description"
                                        }
                                        ,
                                        location: {
                                            from: "location"
                                        }
                                        ,
                                        location_id: {
                                            from: "location_id"
                                        }
                                        ,
                                        groupId: {
                                            from: "groupId", nullable: true
                                        }
                                        , groupName: {
                                            from: "groupName"
                                        }
                                        ,
                                        speakers: {
                                            from: "speakers"
                                        }
                                        ,
                                        taglist: {
                                            from: "taglist"
                                        }
                                        ,
                                        status: {
                                            from: "status"
                                        }
                                        ,
                                        color: {
                                            from: "color"
                                        }
                                        ,
                                        isAllDay: {
                                            type: "boolean", from: "IsAllDay"
                                        },
                                        full: {
                                            type: "boolean", from: "full"
                                        },
                                        session_expire: {
                                            type: "boolean", from: "session_expire"
                                        },
                                        full_queue_open: {
                                            type: "boolean", from: "full_queue_open"
                                        },
                                        seat_availability: {
                                            from: "seat_availability"
                                        },
                                        lang_vat_included: {
                                            from: "lang_vat_included"
                                        },
                                        lang_vat_excluded: {
                                            from: "lang_vat_excluded"
                                        },
                                        cost: {
                                            from: "cost"
                                        },
                                        cost_included_vat: {
                                            from: "cost_included_vat"
                                        },
                                        all_session_status: {
                                            from: "all_session_status"
                                        }
                                    }
                                }
                            }
                        },
                        group: {
                            resources: options.session_scheduler_disable_grouping ? null : ["Groups"]
                        },
                        resources: [
                            {
                                field: "groupId",
                                name: "Groups",
                                dataSource: options.session_scheduler_session_groups
                            }
                        ]
                    });
                    // OPTION SHOW/ HIDDEN
                    if (!options.session_scheduler_show_toolbar_today_button) {
                        $(this).find('.k-nav-today').hide();
                    }
                    if (!options.session_scheduler_show_toolbar_move_day_forward_or_backwards_buttons) {
                        $(this).find('.k-nav-prev').hide();
                        $(this).find('.k-nav-next').hide();
                    }
                    if (!options.session_scheduler_show_toolbar_currently_selected_date) {
                        $(this).find('.k-nav-current').hide();
                    }
                    if (!options.session_scheduler_show_toolbar_change_browse_mode_buttons) {
                        $(this).find('.k-scheduler-views').hide();
                    }
                    if (!options.session_scheduler_show_toolbar_business_hours_toggle) {
                        $(this).find('.k-scheduler-fullday').hide();
                    }
                    if (!options.session_scheduler_show_subscribe_to_calender) {
                        $(this).closest('.event-plugin-session-scheduler').find('.session-subscribe-to-calendar-icon').hide();
                    }
                    if (!options.session_scheduler_show_all_or_my_sessions) {
                        $(this).closest('.event-plugin-session-scheduler').find('.switch-wrapper').hide();
                    }
                    if (!options.session_scheduler_show_session_group_toggle || options.session_scheduler_disable_grouping) {
                        $(this).closest('.event-plugin-session-scheduler').find('.session-group-toggle-list').hide();
                    }
                    if (options.session_scheduler_message) {
                        $(this).closest('.event-plugin-session-scheduler').find('.event-plugin-intro ').find('.elm-message').html(options.session_scheduler_message)
                    }
                    if (options.session_scheduler_title) {
                        $(this).closest('.event-plugin-session-scheduler').find('.event-plugin-intro ').find('.elm-title').html(options.session_scheduler_title)
                    }

                    // GROUP TOGGLE FUNCTIONALITY
                    $(this).closest('.event-plugin-session-scheduler').find('.session-group-toggle-list-item').find('input[type="checkbox"]').change(function (e) {

                        var checked = $.map($this.closest('.event-plugin-session-scheduler').find('.session-group-toggle-list-item').find('input[type="checkbox"]:checked'), function (checkbox) {
                            return parseInt($(checkbox).val());
                        });
                        console.log(checked)
                        var len = $this.closest('.event-plugin-session-scheduler').find('.session-group-toggle-list-item').find('input[type="checkbox"]:checked').length > 0;
                        if (len) {
                            var filter = {
                                logic: "or",
                                filters: $.map(checked, function (value) {
                                    return {
                                        operator: "eq",
                                        field: "value",
                                        value: value
                                    };

                                })
                            };
                        } else {
                            $(this).prop('checked', 'checked');
                            $.growl.warning({message: options.session_scheduler_session_notifications});
                            return false;
                        }
                        var sc = scheduler.data("kendoScheduler");
                        sc.resources[0].dataSource.filter(filter)
                        sc.view(sc.view().name);

                    });

                    // Set Language

                    //$(this).find('.k-nav-today a').text(options.session_scheduler_session_languages.langkey.sessionscheduler_btn_today);
                    ////$(this).find('.k-scheduler-fullday a').text(options.session_scheduler_session_languages.langkey.sessionscheduler_btn_full_day);
                    //$(this).find('.k-scheduler-views').find('[data-name="week"] a').text(options.session_scheduler_session_languages.langkey.sessionscheduler_btn_week);
                    //$(this).find('.k-scheduler-views').find('[data-name="workWeek"] a').text(options.session_scheduler_session_languages.langkey.sessionscheduler_btn_work_week);
                    //$(this).find('.k-scheduler-views').find('[data-name="agenda"] a').text(options.session_scheduler_session_languages.langkey.sessionscheduler_btn_agenda);
                    //$(this).find('.k-scheduler-views').find('[data-name="day"] a').text(options.session_scheduler_session_languages.langkey.sessionscheduler_btn_day);
                    //$(this).closest('.event-plugin-session-scheduler').find('.session-subscribe-to-calendar-icon').text(options.session_scheduler_session_languages.langkey.sessionscheduler_btn_subscribe_sessions);


                    //Switcher

                    $this.closest('.event-plugin-session-scheduler').find('#session-my-session-toggle').change(
                        function () {
                            var checked = $(this).is(':checked');
                            var box_id = $(this).closest('.event-plugin-session-scheduler').find('.box_id').val();
                            var page_id = $(this).closest('.event-plugin-session-scheduler').find('.page_id').val();
                            console.log(checked);
                            console.log(box_id);
                            console.log(page_id);

                            if (checked) {
                                var dataSource = new kendo.data.SchedulerDataSource({
                                    batch: true,
                                    transport: {
                                        read: {
                                            url: base_url + '/get-scheduler-events/?tab=my-session&box_id=' + box_id + '&page_id=' + page_id,
                                            dataType: "json"

                                        }

                                    },
                                    schema: {
                                        model: {
                                            id: "id",
                                            fields: {
                                                id: {
                                                    from: "id", type: "number"
                                                }
                                                ,
                                                title: {
                                                    from: "Title", defaultValue: "No title", validation: {
                                                        required: true
                                                    }
                                                }
                                                ,
                                                start: {
                                                    type: "date", from: "Start"
                                                }
                                                ,
                                                end: {
                                                    type: "date", from: "End"
                                                }
                                                ,
                                                description: {
                                                    from: "Description"
                                                }
                                                ,
                                                location: {
                                                    from: "location"
                                                }
                                                ,
                                                location_id: {
                                                    from: "location_id"
                                                }
                                                ,
                                                groupId: {
                                                    from: "groupId", nullable: true
                                                }
                                                , groupName: {
                                                    from: "groupName"
                                                }
                                                ,
                                                speakers: {
                                                    from: "speakers"
                                                }
                                                ,
                                                taglist: {
                                                    from: "taglist"
                                                }
                                                ,
                                                status: {
                                                    from: "status"
                                                }
                                                ,
                                                color: {
                                                    from: "color"
                                                }
                                                ,
                                                isAllDay: {
                                                    type: "boolean", from: "IsAllDay"
                                                },
                                                full: {
                                                    type: "boolean", from: "full"
                                                },
                                                seat_availability: {
                                                    from: "seat_availability"
                                                },
                                                lang_vat_included: {
                                                    from: "lang_vat_included"
                                                },
                                                lang_vat_excluded: {
                                                    from: "lang_vat_excluded"
                                                },
                                                cost: {
                                                    from: "cost"
                                                },
                                                cost_included_vat: {
                                                    from: "cost_included_vat"
                                                },
                                                all_session_status: {
                                                    from: "all_session_status"
                                                }
                                            }
                                        }
                                    }

                                });
                                var sc = scheduler.data("kendoScheduler");
                                sc.setDataSource(dataSource);
                                dataSource.read();
                            } else {
                                var dataSource = new kendo.data.SchedulerDataSource({
                                    batch: true,
                                    transport: {
                                        read: {
                                            url: base_url + '/get-scheduler-events/?tab=all-session&box_id=' + box_id + '&page_id=' + page_id,
                                            dataType: "json"

                                        }

                                    },
                                    schema: {
                                        model: {
                                            id: "id",
                                            fields: {
                                                id: {
                                                    from: "id", type: "number"
                                                }
                                                ,
                                                title: {
                                                    from: "Title", defaultValue: "No title", validation: {
                                                        required: true
                                                    }
                                                }
                                                ,
                                                start: {
                                                    type: "date", from: "Start"
                                                }
                                                ,
                                                end: {
                                                    type: "date", from: "End"
                                                }
                                                ,
                                                description: {
                                                    from: "Description"
                                                }
                                                ,
                                                location: {
                                                    from: "location"
                                                }
                                                ,
                                                location_id: {
                                                    from: "location_id"
                                                }
                                                ,
                                                groupId: {
                                                    from: "groupId", nullable: true
                                                }
                                                , groupName: {
                                                    from: "groupName"
                                                }
                                                ,
                                                speakers: {
                                                    from: "speakers"
                                                }
                                                ,
                                                taglist: {
                                                    from: "taglist"
                                                }
                                                ,
                                                status: {
                                                    from: "status"
                                                }
                                                ,
                                                color: {
                                                    from: "color"
                                                }
                                                ,
                                                isAllDay: {
                                                    type: "boolean", from: "IsAllDay"
                                                },
                                                full: {
                                                    type: "boolean", from: "full"
                                                },
                                                seat_availability: {
                                                    from: "seat_availability"
                                                },
                                                lang_vat_included: {
                                                    from: "lang_vat_included"
                                                },
                                                lang_vat_excluded: {
                                                    from: "lang_vat_excluded"
                                                },
                                                cost: {
                                                    from: "cost"
                                                },
                                                cost_included_vat: {
                                                    from: "cost_included_vat"
                                                },
                                                all_session_status: {
                                                    from: "all_session_status"
                                                }
                                            }
                                        }
                                    }

                                });
                                var sc = scheduler.data("kendoScheduler");
                                sc.setDataSource(dataSource);
                                dataSource.read();
                            }
                        }
                    );

                });
        } catch (exception) {
            console.log(exception);
            console.log('not ok');

        }


    }
);



