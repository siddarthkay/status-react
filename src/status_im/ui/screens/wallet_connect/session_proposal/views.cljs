(ns status-im.ui.screens.wallet-connect.session-proposal.views
  (:require-macros [status-im.utils.views :refer [defview letsubs]])
  (:require [re-frame.core :as re-frame]
            [status-im.ui.components.react :as react]
            [status-im.i18n.i18n :as i18n]
            [status-im.utils.security]
            [quo.design-system.colors :as colors]
            [quo.core :as quo]
            [status-im.ui.components.icons.icons :as icons]
            [status-im.ui.components.bottom-panel.views :as bottom-panel]
            [status-im.ui.screens.wallet-connect.session-proposal.styles :as styles]
            [status-im.ui.components.list.views :as list]
            [reagent.core :as reagent]
            [clojure.string :as string]))

(defn circle [{:keys [color size style icon icon-size icon-color]}]
  [react/view
   {:style (merge
            style
            {:width            size
             :height           size
             :background-color color
             :border-radius    (/ size 2)
             :align-items      :center
             :justify-content  :center})}
   (when icon
     [icons/icon icon
      (merge
       {:color    (if icon-color icon-color colors/blue)}
       icon-size)])])

(def billfold-icon-container-width 18)

(def billfold-icon-container-height 17.8)

(def chevron-icon-container-width 24)

(def chevron-icon-container-height 24)

(defn toolbar-selection [{:keys [text background-color on-press]}]
  [react/touchable-opacity {:on-press on-press}
   [react/view {:style (styles/toolbar-container background-color)}
    [quo/text {:color :inverse
               :weight :medium
               :style styles/toolbar-text}
     text]
    [icons/icon
     :main-icons/chevron-down
     {:color  (:text-05 @colors/theme)
      :width  chevron-icon-container-width
      :height chevron-icon-container-height}]]])

;; (def selected-account (reagent/atom nil))

(defn render-account [{:keys [address name color] :as account} _ _ {:keys [selected-account]}]
  (let [account-selected? (= (:address @selected-account) address)]
    [react/touchable-without-feedback {:on-press #(reset! selected-account (merge {} account))}
     [react/view {:style {:height 34
                          :background-color color
                          :border-radius 17
                          :padding-horizontal 10
                          :justify-content :center
                          :margin-right 4
                          :opacity (if account-selected? 1 0.5)}}
      [quo/text {:color :inverse
                 :weight (if account-selected? :medium :regular)}
       name]]]))

(defn account-picker [accounts selected-account {:keys [on-press]}]
  (println on-press )
  (if (> (count accounts) 1)
    [react/view {:style {:height 80
                         :width "100%"
                         :justify-content :center
                         :padding-horizontal 16
                         :margin-top 40}}
     [react/view
      [quo/text {:size :small} "Select account"]
      [list/flat-list {:data        accounts
                       :key-fn      :address
                       :render-fn   render-account
                       :render-data {:selected-account selected-account}
                       :horizontal  true
                       :shows-horizontal-scroll-indicator false
                       :extraData @selected-account
                       :style {:height 40
                               :width "100%"
                               :margin-top 10}}]]]
    [react/touchable-opacity {:style {:width "100%"
                                      :align-items :center
                                      :padding-top 8}}
     [toolbar-selection {:text  (:name @selected-account)
                         :background-color (:color @selected-account)
                         :on-press on-press}]]))

(def tiny-circle-size 4)

(def big-circle-size 24)

(defview success-sheet-view [{:keys [peer state topic]}]
  (letsubs [visible-accounts @(re-frame/subscribe [:visible-accounts-without-watch-only])
            dapps-account [:dapps-account]]
           (let [{:keys [accounts]} state
                 {:keys [metadata]} peer
                 {:keys [name icons]} metadata
                 icon-uri (when (and icons (> (count icons) 0)) (first icons))
                 address (last (string/split (first accounts) #":"))
                 account (first (filter #(= (:address %) address) visible-accounts))
                 selected-account (reagent/atom account)]
             [react/view {:style styles/acc-sheet}
              [react/view styles/proposal-sheet-container
               [react/view styles/proposal-sheet-header
                [quo/text {:weight :bold
                           :size   :large}
                 "Connection Request"]]
               [react/image {:style styles/dapp-logo
                             :source {:uri icon-uri}}]
               [react/view styles/sheet-body-container
                [react/view {:style styles/proposal-title-container}
                 [quo/text {:weight :bold
                            :size   :large}
                  name]
                 [quo/text {:weight :regular
                            :size   :large
                            :style  styles/proposal-title}
                  "Connected"]]]
               [account-picker
                (vector dapps-account)
                selected-account
                {:on-press #(println "blur view here")}]
               [quo/text {:weight :regular
                          :color :secondary
                          :style  styles/message-title}
                "Manage connections from within Application Connections"]
               [react/view styles/footer
                [react/view styles/success-button-container
                 [react/view styles/proposal-button-right
                  [quo/button
                   {:theme     :accent
                    :on-press  #(re-frame/dispatch [:hide-wallet-connect-success-sheet])}
                   "Close"]]]]]])))

(def success-sheet
  {:content success-sheet-view})

(defview session-proposal-sheet [{:keys [name icons]}]
  (let [visible-accounts @(re-frame/subscribe [:visible-accounts-without-watch-only])
        dapps-account @(re-frame/subscribe [:dapps-account])
        icon-uri (when (and icons (> (count icons) 0)) (first icons))
        selected-account (reagent/atom dapps-account)]
    [react/view {:style styles/acc-sheet}
     [react/view styles/proposal-sheet-container
      [react/view styles/proposal-sheet-header
       [quo/text {:weight :bold
                  :size   :large}
        "Connection Request"]]
      [react/image {:style styles/dapp-logo
                    :source {:uri icon-uri}}]
      [react/view styles/sheet-body-container
       [react/view {:style styles/proposal-title-container}
        [quo/text {:weight :bold
                   :size   :large}
         (str name " ")]
        [quo/text {:weight :regular
                   :size   :large
                   :style  styles/proposal-title}
         (i18n/label :t/wallet-connect-proposal-title)]]]
      [account-picker visible-accounts selected-account]
      [react/view styles/footer
       [react/view styles/proposal-buttons-container
        [react/view styles/proposal-button-left
         [quo/button
          {:type :secondary
           :on-press #(re-frame/dispatch [:wallet-connect/reject-proposal])}
          (i18n/label :t/reject)]]
        [react/view styles/proposal-button-right
         [quo/button
          {:theme     :accent
           :on-press  #(re-frame/dispatch [:wallet-connect/approve-proposal @selected-account])}
          (i18n/label :t/connect)]]]]]]))

(defview wallet-connect-proposal-sheet []
  (letsubs [proposal-metadata [:wallet-connect/proposal-metadata]]
           [bottom-panel/animated-bottom-panel
            proposal-metadata
            session-proposal-sheet
            #(re-frame/dispatch [:hide-wallet-connect-sheet])]))

(defview wallet-connect-success-sheet-view []
  (letsubs [session [:wallet-connect/session-connected]]
           [bottom-panel/animated-bottom-panel
            session
            success-sheet-view
            #(re-frame/dispatch [:hide-wallet-connect-success-sheet])]))
