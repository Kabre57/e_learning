odoo.define('e_learning_custom.WebClient', function (require) {

    "use strict";

        var AbstractWebClient = require('web.AbstractWebClient');

        AbstractWebClient = AbstractWebClient.include({

            start: function (parent) {

                this.set('title_part', {"zopenerp": "BPCI"});

                this._super(parent);

            },

        });

    });